using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using jobProject.Data;
using jobProject.Models;

namespace jobProject.Controllers
{
    [Authorize]
    public class VacancyController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly UserManager<ApplicationUser> _userManager;

        public VacancyController(ApplicationDbContext context, UserManager<ApplicationUser> userManager)
        {
            _context = context;
            _userManager = userManager;
        }

        // GET: Vacancy
        public async Task<IActionResult> Index()
        {
            var vacancies = await _context.Vacancies
                .Include(v => v.CreatedBy)
                .OrderByDescending(v => v.CreatedDate)
                .ToListAsync();

            return View(vacancies);
        }

        // GET: Vacancy/Details/5
        public async Task<IActionResult> Details(int id)
        {
            var vacancy = await _context.Vacancies
                .Include(v => v.CreatedBy)
                .FirstOrDefaultAsync(v => v.Id == id);

            if (vacancy == null)
                return NotFound();

            var userId = _userManager.GetUserId(User);
            ViewBag.HasApplied = await _context.Applications
                .AnyAsync(a => a.VacancyId == id && a.UserId == userId);

            return View(vacancy);
        }

        // POST: Vacancy/Apply
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Apply(int vacancyId)
        {
            var userId = _userManager.GetUserId(User);

            var existingApplication = await _context.Applications
                .FirstOrDefaultAsync(a => a.VacancyId == vacancyId && a.UserId == userId);

            if (existingApplication != null)
            {
                TempData["Error"] = "Вы уже подали заявку на эту вакансию";
                return RedirectToAction("Details", new { id = vacancyId });
            }

            var application = new Application
            {
                VacancyId = vacancyId,
                UserId = userId,
                AppliedDate = DateTime.UtcNow,
                Status = ApplicationStatus.Pending
            };

            _context.Applications.Add(application);
            await _context.SaveChangesAsync();

            TempData["Success"] = "Заявка успешно подана!";
            return RedirectToAction("MyApplications");
        }

        // GET: Vacancy/MyApplications
        public async Task<IActionResult> MyApplications()
        {
            var userId = _userManager.GetUserId(User);
            var applications = await _context.Applications
                .Include(a => a.Vacancy)
                .Where(a => a.UserId == userId)
                .OrderByDescending(a => a.AppliedDate)
                .ToListAsync();

            return View(applications);
        }
    }
}