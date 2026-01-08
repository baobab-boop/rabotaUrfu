using System;
using System.ComponentModel.DataAnnotations;

namespace jobProject.Models
{
    public class Application
    {
        public int Id { get; set; }

        [Required]
        public int VacancyId { get; set; }
        public virtual Vacancy Vacancy { get; set; }

        [Required]
        public string UserId { get; set; }
        public virtual ApplicationUser User { get; set; }

        public DateTime AppliedDate { get; set; } = DateTime.UtcNow;

        public ApplicationStatus Status { get; set; } = ApplicationStatus.Pending;
        public DateTime? StatusChangedDate { get; set; }
        public string? AdminComment { get; set; }
    }

    public enum ApplicationStatus
    {
        Pending,
        Accepted,
        Rejected
    }
}