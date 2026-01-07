using jobProject.Data;
using jobProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace jobProject.Controllers
{
    [Authorize(Roles = "Admin")]
    public class TestDataController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly UserManager<ApplicationUser> _userManager;

        public TestDataController(ApplicationDbContext context, UserManager<ApplicationUser> userManager)
        {
            _context = context;
            _userManager = userManager;
        }

        [HttpPost]
        public async Task<IActionResult> AddTestData()
        {
            var userId = _userManager.GetUserId(User);

            // Добавляем тестовые вакансии
            var vacancies = new List<Vacancy>
            {
                new Vacancy
                {
                    Title = "Разработчик C#",
                    Description = "Разработка веб-приложений на ASP.NET Core. Требуется опыт работы от 1 года. Знание Entity Framework, SQL, JavaScript.",
                    Location = "Москва, офис",
                    WorkTime = DateTime.Now.AddDays(7),
                    CreatedByUserId = userId,
                    CreatedDate = DateTime.UtcNow
                },
                new Vacancy
                {
                    Title = "Frontend разработчик",
                    Description = "Разработка пользовательских интерфейсов на React/TypeScript. Опыт работы с Redux, Webpack, CSS препроцессорами.",
                    Location = "Санкт-Петербург, гибрид",
                    WorkTime = DateTime.Now.AddDays(14),
                    CreatedByUserId = userId,
                    CreatedDate = DateTime.UtcNow
                },
                new Vacancy
                {
                    Title = "Дизайнер UI/UX",
                    Description = "Создание дизайн-макетов для веб и мобильных приложений. Работа в Figma, Adobe Creative Suite. Опыт создания дизайн-систем.",
                    Location = "Удаленно",
                    WorkTime = DateTime.Now.AddDays(10),
                    CreatedByUserId = userId,
                    CreatedDate = DateTime.UtcNow
                },
                new Vacancy
                {
                    Title = "Менеджер проектов",
                    Description = "Управление командой разработки. Составление планов, контроль сроков, коммуникация с заказчиками. Опыт работы от 2 лет.",
                    Location = "Москва, офис",
                    WorkTime = DateTime.Now.AddDays(21),
                    CreatedByUserId = userId,
                    CreatedDate = DateTime.UtcNow
                },
                new Vacancy
                {
                    Title = "Тестировщик QA",
                    Description = "Ручное и автоматизированное тестирование веб-приложений. Составление тест-кейсов, багрепортов. Знание Selenium, Postman.",
                    Location = "Удаленно",
                    WorkTime = DateTime.Now.AddDays(5),
                    CreatedByUserId = userId,
                    CreatedDate = DateTime.UtcNow
                }
            };

            _context.Vacancies.AddRange(vacancies);
            await _context.SaveChangesAsync();

            TempData["Success"] = "Тестовые вакансии добавлены!";
            return RedirectToAction("ManageVacancies", "Admin");
        }
    }
}