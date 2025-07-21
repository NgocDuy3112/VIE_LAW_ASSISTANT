using Microsoft.AspNetCore.Mvc;
using UserServiceApi.Services;


namespace UserServiceApi.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class AuthController : ControllerBase
    {
        private readonly IUserService _userService;

        public AuthController(IUserService userService) => _userService = userService;

        [HttpPost("register")]
        public async Task<IActionResult> Register(string username, string email, string password)
        {
            var result = await _userService.RegisterAsync(username, email, password);
            if (!result)
                return BadRequest("Email already exists.");

            return Ok("User registered successfully.");
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login(string email, string password)
        {
            var token = await _userService.LoginAsync(email, password);
            if (token == null)
                return Unauthorized("Invalid credentials.");

            return Ok(new { token });
        }
    }
}
