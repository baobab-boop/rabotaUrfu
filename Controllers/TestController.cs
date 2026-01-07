using jobProject.Data;
using Microsoft.AspNetCore.Mvc;

namespace jobProject.Controllers
{
    public class TestController : Controller
    {
        [Route("test")]
        public IActionResult Test()
        {
            return Content("Тестовый контроллер работает!");
        }

        [Route("test/vacancy")]
        public IActionResult TestVacancy()
        {
            return Content("Тест доступа к Vacancy контроллеру");
        }

        [Route("test/db")]
        public IActionResult TestDb([FromServices] ApplicationDbContext context)
        {
            try
            {
                var canConnect = context.Database.CanConnect();
                return Content($"База данных доступна: {canConnect}");
            }
            catch (Exception ex)
            {
                return Content($"Ошибка базы данных: {ex.Message}");
            }
        }
    }
}