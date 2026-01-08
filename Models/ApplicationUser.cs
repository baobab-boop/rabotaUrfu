using Microsoft.AspNetCore.Identity;
using System.Collections.Generic;

namespace jobProject.Models
{
    public class ApplicationUser : IdentityUser
    {
        public string? FullName { get; set; }
        public virtual ICollection<Application> Applications { get; set; } = new List<Application>();
    }
}