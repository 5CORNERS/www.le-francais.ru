from django.views import View
from django.shortcuts import HttpResponse
import json
from django.core.mail import EmailMessage

MESSAGE = '''Добрый день!

Вы активировали урок на сайте le-francais.ru —  поэтому я направил Вам это письмо. Я описал там в двух словах положение дел, но если позволите, я хотел бы добавить несколько слов. Не сочтите за труд, прочтите мои объяснения.

Мы сделали платным доступ к последней части уроков «Для тех, кто хочет продолжать». Я очень хочу, чтобы Вы отнеслись к этому с пониманием. Это было непростое решение, поверьте! Мы до последнего не хотели на это идти, хотя все вокруг нам настойчиво советовали поступить именно так. Мы держались, но обстоятельства просто выкрутили нам руки — и нам пришлось делать выбор: или мы закрываем проект, или мы сохраняем его и развиваем, но вот таким образом.

Закрыть проект, в который вложено десять лет любви и сумасшедшего труда и которым пользуются десятки тысяч человек? У нас просто не поднялась рука.

Сделать платными часть уроков, которые слушает меньше одного процента всех посетителей сайта и для которых это стало если и не частичкой их жизни, то привычным ее дополнением, которые слушают эти уроки уже не первый месяц, а то и не первый год, которые по-настоящему мотивированы и извлекают из этого курса осязаемую пользу для себя и ощутимо при этом экономят — вот путь, который мы сочли справедливым и который выбрали.

Я надеюсь (и верю), что Вы поддержите проект и позволите ему развиваться. Это совсем небольшая жертва с вашей стороны, но она позволит сделать изучение французского еще легче, приятнее и удобнее — и для Вас, и для тех, кто пойдет следом за Вами. Это не просто плата за труд нескольких людей, это — вклад в общий проект, который помог вам и еще много раз поможет другим.

Это просто доброе дело.

Теперь по делу. Есть три важных пункта, которые я должен упомянуть.

Первое. Чтобы переход на новую систему не оказался неожиданным препятствием и Вы могли бы заниматься без перерывов, мы сделали однократную возможность  для первых трех активаций «уйти в минус» — Вы можете три раза активировать уроки с нулевым (или отрицательным) балансом.

Второе. Для пенсионеров, студентов и тех, кто находится в очень стесненном финансовом положении, мы готовы предложить возможность оплачивать уроки по одному по «оптовой» цене. Чтобы перейти в такой режим, напишите нам, любым способом подтвердите свой статус — мы внесем изменения в аккаунт.

Третье. Если Вы в течение последнего года-двух переводили нам деньги без указания Вашего e-mail — так, что мы не можем связать Ваш платеж с Вашим аккаунтом, — напишите нам, пожалуйста, сошлитесь на этот платеж — мы зачтем эту сумму по минимальной цене, каким бы ни был размер Вашего перевода.

Чтобы нам написать, просто ответьте на это письмо. Я допускаю, что в первые дни писем будет много — по нашим прикидкам, тех, кто слушает «старшие» уроки, пара сотен человек (всего на сайте учится ~12 000 человек). Думаю, не у всех будет повод написать, но на всякий случай хочу предупредить, что мы можем тормозить с ответом, буде все таки случится большой входящий поток писем.

Не хочу больше занимать Ваше внимание. Очень рассчитываю на Ваше понимание и готовность нас поддержать. Если Вы хотите чуть подробнее узнать, как все устроено в нашем проекте, почему нам пришлось пойти на этот шаг и какие у нас планы, я написал отдельную страничку на сайте: https://le-francais.ru/explication

Хорошего дня! Учите французский и получайте удовольствие!

Илья Думов
le-francais.ru'''

MESSAGE_FOR_NOT_PAYED = '''Message - 1'''

MESSAGE_FOR_PAYED = '''Message - 2'''


class SawMessageView(View):
	def dispatch(self, request, *args, **kwargs):
		return super(SawMessageView, self).dispatch(request, *args, **kwargs)

	def post(self, request):
		user = request.user
		if request.POST['action'] == 'make_true':
			if user.has_payed():
				msg_body = MESSAGE_FOR_PAYED
				user.add_cups(5)
			else:
				msg_body = MESSAGE_FOR_NOT_PAYED
				user.add_credit_cups(3)
			EmailMessage(
				to=[request.user.email],
				subject='Активация уроков на сайте le-francais.ru',
				body=msg_body,
				from_email='ilia.dumov@files.le-francais.ru',
				reply_to=['support@le-francais.ru']
			).send()
			user.saw_message = True
			user.save()
			return HttpResponse(b'OK', status=200)
		elif request.POST['action'] == 'get_state':
			return HttpResponse(json.dumps(user.saw_message), content_type='application/json', status=200)
		else:
			return HttpResponse(status=400)
