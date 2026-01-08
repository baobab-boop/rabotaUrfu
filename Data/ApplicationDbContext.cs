using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using jobProject.Models;

namespace jobProject.Data
{
    public class ApplicationDbContext : IdentityDbContext<ApplicationUser>
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<Vacancy> Vacancies { get; set; }
        public DbSet<Application> Applications { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Отключаем каскадное удаление для всех связей по умолчанию
            foreach (var relationship in modelBuilder.Model.GetEntityTypes()
                .SelectMany(e => e.GetForeignKeys()))
            {
                relationship.DeleteBehavior = DeleteBehavior.Restrict;
            }

            // Настройка Vacancy
            modelBuilder.Entity<Vacancy>(entity =>
            {
                entity.HasKey(v => v.Id);
                entity.Property(v => v.Title).IsRequired();
                entity.Property(v => v.Description).IsRequired();
                entity.Property(v => v.Location).IsRequired();

                entity.HasOne(v => v.CreatedBy)
                      .WithMany()
                      .HasForeignKey(v => v.CreatedByUserId)
                      .OnDelete(DeleteBehavior.Restrict);
            });

            // Настройка Application
            modelBuilder.Entity<Application>(entity =>
            {
                entity.HasKey(a => a.Id);

                entity.HasOne(a => a.Vacancy)
                      .WithMany(v => v.Applications)
                      .HasForeignKey(a => a.VacancyId)
                      .OnDelete(DeleteBehavior.Restrict);

                entity.HasOne(a => a.User)
                      .WithMany(u => u.Applications)
                      .HasForeignKey(a => a.UserId)
                      .OnDelete(DeleteBehavior.Restrict);
            });
        }
    }
}