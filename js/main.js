var index;

var setup_search = function(documents) {
  $("#search").keyup(function(e) {
    if (e.which !== 13) {
      return;
    }
    var results = index.search(this.value);
    var docs = results.map(function(result) {
        return documents.filter(function(doc) {
          return doc.uri == result.ref;
        })[0];
    });

    var modal_header = $(".modal-header");
    var text = modal_header.text();
    modal_header.text(`Search Results (${results.length})`);

    var modal_body = $(".modal-body");
    modal_body.children().remove();
    docs.forEach(function(doc) {
      var result = $("<p>")
        .append(
          $("<a>")
            .attr("href", doc.uri)
            .text(doc.title)
        )
        .appendTo(modal_body);

      if (doc.author != "<no value>") {
        result.append($("<span style='display: block;'>").text(doc.author));
      }
      if (doc.issue != "<no value>") {
        result.append($("<span style='display: block;'>").text("Issue " + doc.issue));
      }
    });

    $("#search-modal .close").click(function() {
      $("#search-modal").addClass("hide");
    });

    $("#search-modal").removeClass("hide");
    $(document).keydown(function(e) {
      if (e.which === 27) {
        $("#search-modal").addClass("hide");
      }
    });
  });
};

var lumr_index = document.currentScript.getAttribute("data-lumr-index"),
  raw_index = document.currentScript.getAttribute("data-index");

var setup_raw_index = function(documents) {
  console.log("Setting up raw index...");
  index = lunr(function() {
    this.ref("uri");
    this.field("title", { boost: 10 });
    this.field("content");
    documents.map(function(doc) {
      this.add(doc);
    }, this);
    setup_search(documents);
  });
};

var setup_lumr_index = function(data) {
  console.log("Setting up lumr index...");
  index = lunr.Index.load(data);
  $.get(raw_index).success(function(documents) {
    setup_search(documents);
  });
};

$.get(lumr_index)
  .success(setup_lumr_index)
  .fail(function(e) {
    $.get(raw_index)
      .success(setup_raw_index)
      .fail(function(e) {
        console.log("Couldn't load index.json");
        console.log(e);
      });
  });
