using BCrypt.Net;
using UserServiceApi.Models;
using UserServiceApi.Repositories;
using UserServiceApi.Helpers;

namespace UserServiceApi.Services;

public class UserService : IUserService
{
    private readonly IUserRepository _repo;
    private readonly JwtTokenGenerator _jwt;

    public UserService(IUserRepository repo, JwtTokenGenerator jwt)
    {
        _repo = repo;
        _jwt = jwt;
    }

    public async Task<bool> RegisterAsync(string username, string email, string password)
    {
        if (await _repo.GetUserByEmailAsync(email) != null)
            return false;

        var hash = BCrypt.Net.BCrypt.HashPassword(password);
        var user = new User
        {
            Username = username,
            Email = email,
            PasswordHash = hash
        };

        await _repo.AddUserAsync(user);
        return true;
    }

    public async Task<string?> LoginAsync(string email, string password)
    {
        var user = await _repo.GetUserByEmailAsync(email);
        if (user == null || !BCrypt.Net.BCrypt.Verify(password, user.PasswordHash))
            return null;

        return _jwt.GenerateToken(user);
    }
}