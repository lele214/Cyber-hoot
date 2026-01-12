from werkzeug.security import check_password_hash

hash_value = 'scrypt:32768:8:1$vjbiiU83rR1SSJ34$bb17fef05c223ca86fa2704283de689e73698a0f3ffad7533fc2723e901f3e649c7289bb5207e7464bb6a7daea213835e996563087f2777133057e565b1fbff1'
password = 'Admin1234!'

result = check_password_hash(hash_value, password)
print(f"Hash verification result: {result}")

if result:
    print("✓ Le mot de passe correspond au hash !")
else:
    print("✗ Le mot de passe ne correspond PAS au hash !")
