using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using jobProject.Data;
using jobProject.Models;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace jobProject.Controllers
{
    [Authorize(Roles = "Admin")]
    public class AdminController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly UserManager<ApplicationUser> _userManager;

        public AdminController(ApplicationDbContext context, UserManager<ApplicationUser> userManager)
        {
            _context = context;
            _userManager = userManager;
        }

        // GET: Admin/ManageVacancies
        public async Task<IActionResult> ManageVacancies()
        {
            var vacancies = await _context.Vacancies
                .Include(v => v.CreatedBy)
                .OrderByDescending(v => v.CreatedDate)
                .ToListAsync();

            return View(vacancies);
        }

        // GET: Admin/CreateVacancy
        public IActionResult CreateVacancy()
        {
            return View();
        }

        // POST: Admin/CreateVacancy
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> CreateVacancy(Vacancy vacancy, IFormFile imageFile)
        {
            if (ModelState.IsValid)
            {
                if (imageFile != null && imageFile.Length > 0)
                {
                    var fileName = Guid.NewGuid().ToString() + Path.GetExtension(imageFile.FileName);
                    var filePath = Path.Combine("wwwroot/images/vacancies", fileName);

                    Directory.CreateDirectory(Path.GetDirectoryName(filePath));

                    using (var stream = new FileStream(filePath, FileMode.Create))
                    {
                        await imageFile.CopyToAsync(stream);
                    }

                    vacancy.ImageUrl = "/images/vacancies/" + fileName;
                }

                vacancy.CreatedByUserId = _userManager.GetUserId(User);
                vacancy.CreatedDate = DateTime.UtcNow;

                _context.Vacancies.Add(vacancy);
                await _context.SaveChangesAsync();

                return RedirectToAction("ManageVacancies");
            }
            return View(vacancy);
        }

        // GET: Admin/EditVacancy/5
        public async Task<IActionResult> EditVacancy(int id)
        {
            var vacancy = await _context.Vacancies.FindAsync(id);
            if (vacancy == null)
                return NotFound();

            return View(vacancy);
        }

        // POST: Admin/EditVacancy/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> EditVacancy(int id, Vacancy vacancy, IFormFile imageFile)
        {
            if (id != vacancy.Id)
                return NotFound();

            if (ModelState.IsValid)
            {
                try
                {
                    var existingVacancy = await _context.Vacancies.FindAsync(id);
                    if (existingVacancy == null)
                        return NotFound();

                    existingVacancy.Title = vacancy.Title;
                    existingVacancy.Description = vacancy.Description;
                    existingVacancy.Location = vacancy.Location;
                    existingVacancy.WorkTime = vacancy.WorkTime;

                    if (imageFile != null && imageFile.Length > 0)
                    {
                        var fileName = Guid.NewGuid().ToString() + Path.GetExtension(imageFile.FileName);
                        var filePath = Path.Combine("wwwroot/images/vacancies", fileName);

                        Directory.CreateDirectory(Path.GetDirectoryName(filePath));

                        using (var stream = new FileStream(filePath, FileMode.Create))
                        {
                            await imageFile.CopyToAsync(stream);
                        }

                        existingVacancy.ImageUrl = "/images/vacancies/" + fileName;
                    }

                    _context.Update(existingVacancy);
                    await _context.SaveChangesAsync();
                }
                catch (DbUpdateConcurrencyException)
                {
                    if (!VacancyExists(vacancy.Id))
                        return NotFound();
                    else
                        throw;
                }
                return RedirectToAction("ManageVacancies");
            }
            return View(vacancy);
        }

        // POST: Admin/DeleteVacancy/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteVacancy(int id)
        {
            var vacancy = await _context.Vacancies.FindAsync(id);
            if (vacancy != null)
            {
                _context.Vacancies.Remove(vacancy);
                await _context.SaveChangesAsync();
            }
            return RedirectToAction("ManageVacancies");
        }

        // GET: Admin/ManageApplications
        public async Task<IActionResult> ManageApplications(int vacancyId)
        {
            var applications = await _context.Applications
                .Include(a => a.User)
                .Include(a => a.Vacancy)
                .Where(a => a.VacancyId == vacancyId)
                .OrderByDescending(a => a.AppliedDate)
                .ToListAsync();

            ViewBag.VacancyId = vacancyId;
            return View(applications);
        }

        // POST: Admin/UpdateApplicationStatus
        [HttpPost]
        public async Task<IActionResult> UpdateApplicationStatus(int applicationId, ApplicationStatus status, string adminComment)
        {
            var application = await _context.Applications
                .Include(a => a.User)
                .FirstOrDefaultAsync(a => a.Id == applicationId);

            if (application == null)
                return NotFound();

            application.Status = status;
            application.StatusChangedDate = DateTime.UtcNow;
            application.AdminComment = adminComment;

            _context.Update(application);
            await _context.SaveChangesAsync();

            return RedirectToAction("ManageApplications", new { vacancyId = application.VacancyId });
        }

        private bool VacancyExists(int id)
        {
            return _context.Vacancies.Any(e => e.Id == id);
        }
    }
}