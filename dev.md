To check for broken links

```sh
hugo; ./bin/htmltest public/
```


To update a broken article

```sh
./scripts/downloader.py --issue 30 --force
./scripts/make-magazine.py --article archive/issue030_jeff_eastham_anderson.aspx
```


To update archive branch with newly downloaded data:

```sh
git add archive
git stash
git checkout archive
git stash pop
# Commit the changes
git checkout master
git checkout archive -- archive
git reset
```
