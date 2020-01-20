import sys
import bcrypt

#hashed password created by the companionprogram
username = 'test'
hashedpass = b'$2b$14$ZNa331bLHBnQe0aAej5cVeYJcxuZvbRGdXCUoMqz/ze7v2rRAO.s6'


#this function creates the above hashedpass for a given password
#if invoked as a script
#copy the hashedpass printed to the above variable
def hashpass(argv):
   argc = len(sys.argv);
   if ( argc < 2 ):
     print ("Usage: "+sys.argv[0]+" password")
     sys.exit(0);

   password = sys.argv[1]
   password = password.encode("utf-8");
   #create a hash of the password
   hashed = bcrypt.hashpw(password, bcrypt.gensalt(14))
   print("username=",username)
   print("hashedpass=",hashed)
   if not bcrypt.checkpw(password, hashed):
    print("does not match")


if __name__ == "__main__" :
 
    hashpass(sys.argv)
