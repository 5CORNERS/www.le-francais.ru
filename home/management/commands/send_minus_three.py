import datetime

from django.core.mail import EmailMessage
from django.core.management import BaseCommand

from custom_user.models import User
from home.models import UserLesson
from tinkoff_merchant.models import Payment

TABLE = {
	"ikka-2008@mail.ru": ", Ирина",
	"natalybut@gmail.com": "",
	"constantinitin@gmail.com": ", Константин",
	"alexandra.baranova@me.com": ", Александра",
	"hasmik.asa@yandex.ru": ", Хасмик",
	"andante.vg@gmail.com": ", Виктория",
	"svetlana02031962@gmail.com": ", Светлана",
	"ivcn121@gmail.com": ", Нина",
	"k-i-n-a-@mail.ru": "",
	"oinozemtsevkld@gmail.com": ", Олег",
	"valeriatetarchuk@gmail.com": ", Лера",
	"inga.or@yandex.ru": ", Инга",
	"jesuislada@yandex.ru": "",
	"tzvetkova.anna@yandex.ru": ", Анна",
	"fplay.tm@mail.ru": "",
	"ofilipok@gmail.com": ", Оля",
	"goldman.svetlana@mail.ru": "",
	"anna_1barrister@mail.ru": "",
	"deadlyalex@mail.ru": "",
	"bunlesque8@gmail.com": ", Лилиана",
	"alexgladilin@rambler.ru": ", Алексей",
	"milkman3005@rambler.ru": "",
	"elgrach@yandex.ru": ", Елена",
	"innakapl@mail.ru": ", Инна",
	"serafima-michalchenko@mail.ru": "",
	"lanagoron@gmx.de": ", Лана",
	"olga54_kr@mail.ru": ", Ольга",
	"krispinpin@mail.ru": "",
	"bunescua46@gmail.com": ", Анастасия",
	"iulian.bunescu56@gmail.com": "",
	"redko.victor1963@gmail.com": ", Виктор",
	"christina.zhigrina@gmail.com": ", Кристина",
	"kristinochka2312@mail.ru": ", Кристина",
	"andreibunescu579@gmail.com": ", Андрей",
	"elena9030985553@yandex.ru": "",
	"bookbinder64@yandex.ru": "",
	"sergejgalagan766@gmail.com": ", Сергей",
	"Pica.picasso@yandex.ru": "",
	"kuzenko.oleg@gmail.com": ", Олег",
	"lyuba.karachun.55@mail.ru": ", Любовь",
	"anya.kan.92@mail.ru": "",
	"iramiller1994@mail.ru": "",
	"katena.koroleva.2020@mail.ru": "",
	"olegs.2020@mail.ru": "",
	"olgane96@mail.ru": "",
	"ivan.sidorenko.1212@mail.ru": "",
	"larak.2019@mail.ru": "",
	"svetasvet2020@mail.ru": "",
	"dimadi9393@mail.ru": "",
	"igor.starkov.83@mail.ru": "",
	"lora.di.00@mail.ru": "",
	"isotnicova@mail.ru": "",
	"isa.ii.84@mail.ru": "",
	"egor.nemov.81@mail.ru": "",
	"sara.sari.rad@mail.ru": "",
	"petrkir95@mail.ru": "",
	"inna.paki.pak@mail.ru": "",
	"jon.van.01@mail.ru": "",
	"lola.la.2000@mail.ru": "",
	"travaille12@yandex.ru": "",
	"mari.mar.2020@mail.ru": "",
	"travaille13@yandex.ru": "",
	"polina.pol.98@mail.ru": "",
	"nina.na.86@mail.ru": "",
	"lenkakolen01@mail.ru": "",
	"lina.melnic.83@mail.ru": "",
	"rina.ri.93@mail.ru": "",
	"nika.neo.83@mail.ru": "",
}

MESSAGE = '''Добрый день{0}!

Я заметил, что Вы слушаете «старшие» уроки, совершили три кредитных активации — и бросили занятия.

Возможно, это связанно с затруднениями, не позволяющими Вам приобрести абонемент сразу на много уроков, в то время как «поштучно» активации стоят для Вас дорого? 

Мне бы не хотелось, чтобы это стало для Вас непреодолимым препятствием в изучении языка. Мы в инициативном порядке перевели Вас в особый скидочный режим, который позволит Вам приобретать активации даже поштучно по цене урока в большом абонементе. Это значит, что стоимость одного «билетика» будет почти в два раза ниже. Если теперь Вы зайдете в раздел «Пополнить запасы» (это в меню в самом правом пункте с Вашим именем), Вы увидите другие стоимости абонементов и другую стоимость одного урока.

Кроме этого, мы простили Вашу задолженность по активациям — Вы начнете с чистого листа.

Я очень расчитываю на то, что Вы с пониманием отнесетесь к тем мерам, на которые мы вынуждены были пойти, чтобы оплачивать наши расходы по содержанию проекта, и поддержите нас в этом очень непростом деле.

Учите французский, не останавливайтесь, оставайтесь с нами! И не стесняйтесь писать, если у Вас возникнуть вопросы!

С надеждой на Ваше возвращение,

Илья Думов
le-francais.ru

P.S. Оплачивать можно картами, выпущенными в любой валюте и из любой страны — сумма будет пересчитана по курсу в валюту карты автоматически.'''

def find_users():
	users = list(User.objects.filter(_cup_amount=-3))
	l = []
	not_l = []
	for u in users:
		if not Payment.objects.filter(customer_key=u.id, status='CONFIRMED') | Payment.objects.filter(customer_key=u.id, status='AUTHORIZED'):
			l.append(u)
		else:
			not_l.append(u)
	return l

def get_max_min(user):
	activations = UserLesson.objects.filter(user=user)
	datelist = []
	for a in activations:
		datelist.append(a.date)
	return max(datelist), min(datelist)

def get_times(user):
	activations = UserLesson.objects.filter(user=user)
	datetimes = []
	for a in activations:
		datetimes.append(a.date)
	timedeltas = []
	for i in range(1, len(datetimes)):
		timedeltas.append(datetimes[i] - datetimes[i-1])
	average_timedelta = sum(timedeltas, datetime.timedelta(0)) / len(timedeltas)
	all_timedelta = datetimes[-1] - datetimes[0]
	from_today = datetime.datetime.now(datetime.timezone.utc) - datetimes[-1]
	return datetimes, average_timedelta, all_timedelta, from_today

def lookup(user):
	table = TABLE
	if user.email in table.keys():
		return table[user.email]
	else:
		return ''

class Command(BaseCommand):
	def handle(self, *args, **options):
		for u in find_users():
			datetimes, average_timedelta, all_timedelta, from_today = get_times(u)

			message = EmailMessage(
				to=[u.email],
				subject='',
				body=MESSAGE.format(lookup(u)),
				from_email='ilia.dumov@files.le-francais.ru',
				reply_to=['support@le-francais.ru'],
			)
			if from_today.days > 13:
				u.switch_low_price()
				u.add_cups(3)
				message.send()
		print('Done')
