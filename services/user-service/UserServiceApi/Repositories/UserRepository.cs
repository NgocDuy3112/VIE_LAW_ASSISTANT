using Microsoft.EntityFrameworkCore;
using UserServiceApi.Models;
using UserServiceApi.Database;


namespace UserServiceApi.Repositories;

public class UserRepository: IUserRepository
{
    private readonly AppDbContext _context;
    public UserRepository(AppDbContext context) => _context = context;

    public async Task<User?> GetUserByEmailAsync(string email)
        => await _context.Users.FirstOrDefaultAsync(u => u.Email == email);

    public async Task AddUserAsync(User user)
    {
        _context.Users.Add(user);
        await _context.SaveChangesAsync();
    }

}
