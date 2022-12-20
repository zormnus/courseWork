import bcrypt

hash = bcrypt.hashpw('dyrdom1'.encode(), bcrypt.gensalt()).decode()
print(hash)