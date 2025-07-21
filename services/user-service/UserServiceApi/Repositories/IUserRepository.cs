using System;
using UserServiceApi.Models;

namespace UserServiceApi.Repositories;

public interface IUserRepository
{
    Task<User?> GetUserByEmailAsync(string email);
    Task AddUserAsync(User user);
}
