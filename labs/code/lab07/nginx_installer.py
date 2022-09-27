from fabric import Connection
import credentials as cred
import os


def install_nginx(c, stud_nr):
    c.sudo('apt install nginx -y')
    os.system(f'scp ./default lab07-{stud_nr}:/home/ubuntu')
    c.sudo('mv /home/ubuntu/default /etc/nginx/sites-enabled/')
    c.sudo('service nginx restart')


def install_django(c):
    c.sudo('mkdir -p ~/opt/wwc/mysites')
    c.sudo('apt install python3-pip -y')
    c.run('pip3 install django')
    c.run('django-admin startproject lab')
    c.run('cd ./lab && python3 manage.py startapp polls')
    c.sudo('mv ./lab ~/opt/wwc/mysites')


if __name__ == '__main__':
    stud_nr = str(cred.STUD_NR)
    c = Connection(f'lab07-{stud_nr}')
    c.sudo('apt update -y')
    c.sudo('apt upgrade -y')
    install_django(c)
    install_nginx(c, stud_nr)
    c.sudo('python3 ~/opt/wwc/mysites/lab/manage.py runserver 8000 &')
