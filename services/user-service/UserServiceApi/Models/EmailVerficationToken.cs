using System.ComponentModel.DataAnnotations;

namespace UserServiceApi.Models;

public class EmailVerficationToken
{
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    public Guid UserId { get; set; }

    [Required]
    public string Token { get; set; } = string.Empty;

    public DateTime ExpiresAt { get; set; }

    public bool IsUsed { get; set; } = false;
}
