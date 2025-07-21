using Microsoft.EntityFrameworkCore;
using UserServiceApi.Models;


namespace UserServiceApi.Database;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users { get; set; }
    
}
