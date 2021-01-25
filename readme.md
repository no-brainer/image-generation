# Male face generation

![It ain't much but it's honest work](https://i.kym-cdn.com/entries/icons/original/000/028/021/work.jpg)

### Collecting the data
My data collection script shows its user an image, then user has to select a square region with an 
appropriate object. Selected region is resized to fixed size and added into a zip file.

When you are cropping out the images, you can press `q` to quit, 
`d` to go to the next image or `s` to go to the next query.

The list of google search queries that will be used should be put in `queries.txt` file, that is placed in 
`data_collection` folder. If this is somehow inconvenient, you can also simply change the path in 
`data_collection/utils/query_queue.py`.

Data zip is in `imgs` folder, so you will probably need to create it. This behavior can also be changed in
`data_collection/main.py`.

