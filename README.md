# Challenge 2 - scripting

The idea is to generate an script whitch acts as an interface to the Art Institute of Chicago API <https://api.artic.edu/docs/>

## How to use
### requirements
* verify you have python installed
* install dependencies

  ```
  pip install -r requirements.txt
  ```
### basic use
To use this script call
```
  python3 artworks.py --search cats
```
in case you use windows call "python" instead of "python3" on the line above
the result should be a message like this:
```
  JSON generated as artworks.json
```
You can type 
```
  python3 artworks.py -h
```
to see how to use diferent flags
### sending mail
To use this option you will need to put your the sender credentials into a file called <.credentials.txt>

```
  xxx xxx xxx
  your.email@gmail.com
```
the first line with your mail token

the second with your e-mail direction
 
This section only works with a gmail account

### How to generate my mail token?
