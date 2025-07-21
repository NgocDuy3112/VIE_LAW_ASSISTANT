using Microsoft.AspNetCore.Identity;

namespace UserServiceApi.Helpers;

public class PasswordHasher
{
    private static readonly PasswordHasher<string> hasher = new PasswordHasher<string>();

    public static string Hash(string password) => hasher.HashPassword(string.Empty, password);

    public static bool Verify(string hashedPassword, string password)
        => hasher.VerifyHashedPassword(string.Empty, hashedPassword, password) == PasswordVerificationResult.Success;
}
