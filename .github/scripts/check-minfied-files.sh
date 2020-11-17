
cd ../../utils/minify_plugins/

npm install

npm run minify

if ! git diff-index --quiet HEAD --; then
    echo "The minifiy files are not updated";
    exit 1;
fi