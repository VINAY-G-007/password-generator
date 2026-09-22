import secrets
import string


L=int(input("Enter length of the PASSWORD: "))
A,B,C,D=input("Enter your preference. upper_case ? (Y/N), lower_case? (Y/N), digits? (Y/N), symbols? (Y/N) : ").split(",")


def generate_password(L,A,B,C,D):
    pool=""
    password=""
    if A.strip().upper()=="Y": # stripe removes any leading and trailing whitespace characters from the string, and upper() converts the string to uppercase. This ensures that the comparison is case-insensitive and ignores any accidental spaces in the input.
        pool+=string.ascii_uppercase
    if B.strip().upper()=="Y":
        pool+=string.ascii_lowercase
    if C.strip().upper()=="Y":
        pool+=string.digits
    if D.strip().upper()=="Y":
        pool+=string.punctuation
    if pool=="":
        print("Please select at least one option")
        return None


    for i in range(L):
        password+=secrets.choice(pool)  # secretaly choosing a character from the pool  

    return password

generated_password=generate_password(L,A,B,C,D)

if generated_password:
    print(f" GENERATED PASSWORD : {generated_password}")



