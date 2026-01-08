using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace jobProject.Models
{
    public class Vacancy
    {
        public int Id { get; set; }

        [Required]
        public string Title { get; set; }

        [Required]
        public string Description { get; set; }

        [Required]
        public string Location { get; set; }

        public DateTime WorkTime { get; set; }

        public string? ImageUrl { get; set; }

        public DateTime CreatedDate { get; set; } = DateTime.UtcNow;

        public string? CreatedByUserId { get; set; }
        public virtual ApplicationUser? CreatedBy { get; set; }

        public virtual ICollection<Application> Applications { get; set; } = new List<Application>();
    }
}