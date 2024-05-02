# sepdfcsv - simple pdf to csv processor, with docker builder and flask web interface

## Install it as docker image & run (needs 2 repos (1 - program iself 2-cache-serv) Needs docker installed and run.

    $ mkdir my_prog
    
    $ cd my_prog/
    
    $ git clone https://github.com/pehks1980/sepdfcsv.git <----- repo 1
    
    Cloning into 'sepdfcsv'...
    
    $ cd sepdfcsv/main/
    
    $ git clone https://github.com/pehks1980/cache-serv.git <----------repo 2
    
    Cloning into 'cache-serv'...
    
    $ ls -l
    total 76
    drwxrwxr-x 9 user user 4096 May  2 14:54 ./
    drwxrwxr-x 4 user user 4096 May  2 14:53 ../
    drwxrwxr-x 6 user user 4096 May  2 14:54 cache-serv/ <---sub repo with cache-server here
    drwxrwxr-x 2 user user 4096 May  2 14:53 flask_session/
    -rw-rw-r-- 1 user user   25 May  2 14:53 local_conf.py
    -rw-rw-r-- 1 user user 6696 May  2 14:53 main.py
    drwxrwxr-x 2 user user 4096 May  2 14:53 msg/
    -rw-rw-r-- 1 user user  635 May  2 14:53 mycache.py
    -rw-rw-r-- 1 user user 2289 May  2 14:53 mycache1.py
    drwxrwxr-x 2 user user 4096 May  2 14:53 pdf/
    drwxrwxr-x 2 user user 4096 May  2 14:53 result/
    -rw-rw-r-- 1 user user 4553 May  2 14:53 semsgpdf.py
    -rw-rw-r-- 1 user user 9823 May  2 14:53 sepdfcsv.py
    drwxrwxr-x 2 user user 4096 May  2 14:53 static/
    drwxrwxr-x 2 user user 4096 May  2 14:53 templates/
    
    $ cd ..
    
    $ ls -l
    total 24
    -rw-rw-r-- 1 user user 1409 May  2 14:53 Dockerfile  <--docker file
    -rw-rw-r-- 1 user user   86 May  2 14:53 README.md
    -rwxrwxr-x 1 user user  389 May  2 14:53 gunicorn.sh
    drwxrwxr-x 9 user user 4096 May  2 14:54 main
    -rw-rw-r-- 1 user user  290 May  2 14:53 requirements.old
    -rw-rw-r-- 1 user user 1035 May  2 14:53 requirements.txt
    
    $ docker build -t sepdfcsv .
    
    ......pandas numpy takes a lot to get..... on Mac it takes  > 10 min
    
    
    #run resulted image as docker conatainer
    
    $ docker run -p 8999:8080 -e FLASK_SECRET_KEY=password sepdfcsv 
    
    ... combined log goes here ...
    
    
  ## open on this system browser with address to use it as web
    
  http://127.0.0.1:8999/

# Use web:

File Upload - select all tax invoices files (.PDF or .MSG) or one .PDF file with several pages: tick checkbox in that case

Run - start processing 

Result - get CSV file to import it to Excel. A zip file contains Pdf files extracted from .MSG
