# -*- coding: utf-8 -*-
"""Generate donate.html for all six locales.

Header and footer are lifted verbatim from that locale's existing
yard-sign.html (so nav labels, brand sub-line and the 211B.04 disclaimer stay
byte-identical to what is already live), with the language switcher repointed
at donate.html. The six donor rules and the fine-print summary are lifted from
that locale's brendan.html donate section for the same reason -- they are
already reviewed copy, and retranslating them would only introduce drift.
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXEC = ('https://script.google.com/macros/s/'
        'AKfycbxPDsHZ_1OpB_EagRZlwQsmgfSKjpnKCMVuWtyh-_XKyAR79mk5xRHOu-AT2dp4Fj9c/exec')
PAYPAL = 'https://www.paypal.com/donate/?hosted_button_id=AQT4DAFUX3UTL'

LOCALES = ['en', 'es', 'fr', 'ru', 'so', 'vi']
OG = {'en': 'en_US', 'es': 'es_ES', 'fr': 'fr_FR', 'ru': 'ru_RU',
      'so': 'so_SO', 'vi': 'vi_VN'}

S = {}

S['en'] = dict(
    title='Donate — Ali Verney &amp; Brendan Van Alstyne for Shakopee City Council',
    desc='Support the Verney &amp; Van Alstyne campaign for Shakopee City Council. No corporate money, no big donors.',
    lede='No corporate money and no big donors &mdash; this campaign runs on neighbors chipping in what they can, and every dollar stays right here in Shakopee.',
    intro='Minnesota requires us to report the name, address and employer of anyone whose giving passes $100 in a year. PayPal cannot ask for all of it, so we do &mdash; once, here. It takes about a minute, and then you are straight on to checkout.',
    legend_who="Who's giving", legend_addr='Your mailing address',
    legend_affirm='Three things the law needs you to confirm', legend_else='Anything else?',
    l_name='Your full name', h_name='Use the same name your payment will be under, so we can match the two.',
    l_email='Email', h_email='Only so we can reach you if something does not add up at filing time.',
    h_addr='This goes on a public campaign finance report if your giving passes $100 in a year. That is state law, not our choice.',
    l_street='Street address', l_city='City', l_state='State', l_zip='ZIP',
    l_emp='Employer', h_emp='Or your occupation if you are self-employed, or just &ldquo;not employed&rdquo; &mdash; retired and student both count.',
    a1="I'm a U.S. citizen or a lawfully admitted permanent resident.",
    a2='This is my own money, from a personal account &mdash; not a business or corporate account.',
    a3="Including this gift, I haven't given more than $600 to this committee in 2026.",
    l_note='Optional &mdash; anything you want Brendan to know',
    submit='Continue to payment', sending='One moment…',
    privacy='Your name, address and employer go on a public campaign finance report, because state law says they must. Your email does not &mdash; that stays with the campaign, and we do not sell it, trade it, or hand it to anyone else.',
    ok_h='Thank you &mdash; one more step.',
    ok_b='We have what Minnesota requires us to report. Now finish your donation with PayPal:',
    ok_btn='Continue to PayPal',
    ok_note='No PayPal account needed &mdash; any debit or credit card works. Please give under the same name you just entered, so we can match your gift to what you told us.',
    err_h="That didn't go through.",
    err_b='Something on our end failed, and we would rather you did not lose the donation over it. Please email {EMAIL} or call or text {PHONE} and we will sort it out.',
    unconf='<strong>Online giving is not switched on yet.</strong> Checks work today: make yours payable to <strong>Brendan V for Shakopee</strong> and email {EMAIL} or text {PHONE} for the mailing address. Please include your name, address, and employer with the check.',
    volunteer_line="Can't give right now? <a href=\"volunteer.html\">Volunteering</a> is worth more than money in a race this size.")

S['es'] = dict(
    title='Donar — Ali Verney y Brendan Van Alstyne para el Concejo Municipal de Shakopee',
    desc='Apoya la campaña de Verney y Van Alstyne para el Concejo Municipal de Shakopee. Sin dinero de empresas, sin grandes donantes.',
    lede='Sin dinero de empresas y sin grandes donantes &mdash; esta campaña funciona gracias a vecinos que aportan lo que pueden, y cada dólar se queda aquí mismo, en Shakopee.',
    intro='Minnesota exige que reportemos el nombre, la dirección y el empleador de toda persona cuyas donaciones superen los $100 en un año. PayPal no puede pedir todo eso, así que lo pedimos nosotros &mdash; una sola vez, aquí. Toma alrededor de un minuto y enseguida pasa al pago.',
    legend_who='Quién dona', legend_addr='Su dirección postal',
    legend_affirm='Tres cosas que la ley necesita que confirme', legend_else='¿Algo más?',
    l_name='Su nombre completo', h_name='Use el mismo nombre que aparecerá en su pago, para que podamos relacionarlos.',
    l_email='Correo electrónico', h_email='Solo para poder comunicarnos si algo no cuadra al momento de presentar el informe.',
    h_addr='Esto aparece en un informe público de finanzas de campaña si sus donaciones superan los $100 en un año. Es la ley estatal, no una decisión nuestra.',
    l_street='Dirección', l_city='Ciudad', l_state='Estado', l_zip='Código postal',
    l_emp='Empleador', h_emp='O su ocupación si trabaja por cuenta propia, o simplemente &laquo;no empleado&raquo; &mdash; jubilado y estudiante también cuentan.',
    a1='Soy ciudadano estadounidense o residente permanente legal.',
    a2='Este es mi propio dinero, de una cuenta personal &mdash; no de una cuenta comercial o de empresa.',
    a3='Incluyendo esta donación, no he dado más de $600 a este comité en 2026.',
    l_note='Opcional &mdash; lo que quiera que Brendan sepa',
    submit='Continuar al pago', sending='Un momento…',
    privacy='Su nombre, dirección y empleador aparecen en un informe público de finanzas de campaña, porque la ley estatal lo exige. Su correo electrónico no &mdash; ese se queda con la campaña, y no lo vendemos, ni lo intercambiamos, ni se lo damos a nadie.',
    ok_h='Gracias &mdash; un paso más.',
    ok_b='Ya tenemos lo que Minnesota exige que reportemos. Ahora complete su donación con PayPal:',
    ok_btn='Continuar a PayPal',
    ok_note='No hace falta tener cuenta de PayPal &mdash; funciona cualquier tarjeta de débito o crédito. Por favor done con el mismo nombre que acaba de escribir, para que podamos relacionar su donación con lo que nos dijo.',
    err_h='Eso no se envió.',
    err_b='Algo falló de nuestro lado, y preferimos que no pierda la donación por eso. Escriba a {EMAIL} o llame o mande un mensaje al {PHONE} y lo resolvemos.',
    unconf='<strong>Las donaciones en línea todavía no están activas.</strong> Los cheques funcionan desde hoy: haga el suyo a nombre de <strong>Brendan V for Shakopee</strong> y escriba a {EMAIL} o mande un mensaje al {PHONE} para pedir la dirección postal. Por favor incluya su nombre, dirección y empleador con el cheque.',
    volunteer_line='¿No puede donar ahora? <a href="volunteer.html">Ser voluntario</a> vale más que el dinero en una elección de este tamaño.')

S['fr'] = dict(
    title='Faire un don — Ali Verney et Brendan Van Alstyne pour le conseil municipal de Shakopee',
    desc='Soutenez la campagne Verney et Van Alstyne pour le conseil municipal de Shakopee. Pas d’argent d’entreprise, pas de gros donateurs.',
    lede='Pas d’argent d’entreprise et pas de gros donateurs &mdash; cette campagne vit de voisins qui donnent ce qu’ils peuvent, et chaque dollar reste ici, à Shakopee.',
    intro='Le Minnesota exige que nous déclarions le nom, l’adresse et l’employeur de toute personne dont les dons dépassent 100&nbsp;$ par an. PayPal ne peut pas tout demander, alors nous le faisons &mdash; une seule fois, ici. Cela prend environ une minute, puis vous passez directement au paiement.',
    legend_who='Qui donne', legend_addr='Votre adresse postale',
    legend_affirm='Trois choses que la loi vous demande de confirmer', legend_else='Autre chose&nbsp;?',
    l_name='Votre nom complet', h_name='Utilisez le même nom que celui de votre paiement, afin que nous puissions faire le lien.',
    l_email='Courriel', h_email='Uniquement pour vous joindre si quelque chose ne concorde pas au moment de la déclaration.',
    h_addr='Cette information figure dans un rapport public de financement de campagne si vos dons dépassent 100&nbsp;$ par an. C’est la loi de l’État, pas notre choix.',
    l_street='Adresse', l_city='Ville', l_state='État', l_zip='Code postal',
    l_emp='Employeur', h_emp='Ou votre profession si vous êtes à votre compte, ou simplement «&nbsp;sans emploi&nbsp;» &mdash; retraité et étudiant comptent aussi.',
    a1='Je suis citoyen américain ou résident permanent légal.',
    a2='C’est mon propre argent, provenant d’un compte personnel &mdash; et non d’un compte d’entreprise.',
    a3='Y compris ce don, je n’ai pas donné plus de 600&nbsp;$ à ce comité en 2026.',
    l_note='Facultatif &mdash; ce que vous souhaitez dire à Brendan',
    submit='Continuer vers le paiement', sending='Un instant…',
    privacy='Votre nom, votre adresse et votre employeur figurent dans un rapport public de financement de campagne, parce que la loi de l’État l’exige. Pas votre courriel &mdash; il reste avec la campagne, et nous ne le vendons pas, ne l’échangeons pas et ne le transmettons à personne.',
    ok_h='Merci &mdash; encore une étape.',
    ok_b='Nous avons ce que le Minnesota exige que nous déclarions. Terminez maintenant votre don avec PayPal&nbsp;:',
    ok_btn='Continuer vers PayPal',
    ok_note='Aucun compte PayPal n’est nécessaire &mdash; toute carte de débit ou de crédit fonctionne. Donnez sous le même nom que celui que vous venez d’indiquer, afin que nous puissions faire le lien.',
    err_h='Cela n’a pas fonctionné.',
    err_b='Quelque chose a échoué de notre côté, et nous préférons que vous ne perdiez pas votre don pour autant. Écrivez à {EMAIL} ou appelez ou envoyez un message au {PHONE} et nous arrangerons cela.',
    unconf='<strong>Les dons en ligne ne sont pas encore activés.</strong> Les chèques fonctionnent déjà&nbsp;: libellez le vôtre à l’ordre de <strong>Brendan V for Shakopee</strong> et écrivez à {EMAIL} ou envoyez un message au {PHONE} pour obtenir l’adresse postale. Veuillez indiquer vos nom, adresse et employeur avec le chèque.',
    volunteer_line='Vous ne pouvez pas donner maintenant&nbsp;? <a href="volunteer.html">Devenir bénévole</a> vaut plus que l’argent dans une élection de cette taille.')

S['ru'] = dict(
    title='Пожертвовать — Али Верни и Брендан Ван Алстайн в городской совет Shakopee',
    desc='Поддержите кампанию Верни и Ван Алстайна в городской совет Shakopee. Никаких корпоративных денег и крупных спонсоров.',
    lede='Никаких корпоративных денег и крупных спонсоров &mdash; эта кампания живёт за счёт соседей, которые вносят столько, сколько могут, и каждый доллар остаётся здесь, в Шакопи.',
    intro='Миннесота требует указывать имя, адрес и работодателя каждого, чьи пожертвования за год превысили $100. PayPal не может запросить всё это, поэтому спрашиваем мы &mdash; один раз, здесь. Это занимает около минуты, после чего вы сразу перейдёте к оплате.',
    legend_who='Кто жертвует', legend_addr='Ваш почтовый адрес',
    legend_affirm='Три вещи, которые по закону нужно подтвердить', legend_else='Что-нибудь ещё?',
    l_name='Ваше полное имя', h_name='Укажите то же имя, на которое будет оформлен платёж, чтобы мы смогли их сопоставить.',
    l_email='Электронная почта', h_email='Только чтобы связаться с вами, если при подготовке отчёта что-то не сойдётся.',
    h_addr='Эти данные попадут в публичный отчёт о финансировании кампании, если ваши пожертвования за год превысят $100. Так требует закон штата — это не наш выбор.',
    l_street='Улица и дом', l_city='Город', l_state='Штат', l_zip='Почтовый индекс',
    l_emp='Работодатель', h_emp='Или род занятий, если вы работаете на себя, либо просто «не работаю» &mdash; пенсионер и студент тоже подходят.',
    a1='Я гражданин США или законно принятый постоянный житель.',
    a2='Это мои собственные деньги с личного счёта &mdash; не с делового или корпоративного.',
    a3='С учётом этого взноса я пожертвовал этому комитету не более $600 в 2026 году.',
    l_note='Необязательно &mdash; что вы хотели бы сообщить Брендану',
    submit='Перейти к оплате', sending='Одну минуту…',
    privacy='Ваше имя, адрес и работодатель попадают в публичный отчёт о финансировании кампании, потому что этого требует закон штата. Ваша почта &mdash; нет: она остаётся у кампании, мы не продаём её, не обмениваем и никому не передаём.',
    ok_h='Спасибо &mdash; остался один шаг.',
    ok_b='У нас есть всё, что Миннесота требует указать в отчёте. Теперь завершите пожертвование через PayPal:',
    ok_btn='Перейти в PayPal',
    ok_note='Аккаунт PayPal не нужен &mdash; подойдёт любая дебетовая или кредитная карта. Пожалуйста, жертвуйте под тем же именем, которое вы только что указали, чтобы мы смогли сопоставить платёж.',
    err_h='Отправить не удалось.',
    err_b='Что-то сломалось на нашей стороне, и мы не хотим, чтобы из-за этого пропало ваше пожертвование. Напишите на {EMAIL} или позвоните либо отправьте сообщение на {PHONE}, и мы всё уладим.',
    unconf='<strong>Онлайн-пожертвования пока не подключены.</strong> Чеки принимаются уже сегодня: выпишите чек на <strong>Brendan V for Shakopee</strong> и напишите на {EMAIL} или отправьте сообщение на {PHONE}, чтобы узнать почтовый адрес. Пожалуйста, укажите вместе с чеком своё имя, адрес и работодателя.',
    volunteer_line='Не можете пожертвовать сейчас? <a href="volunteer.html">Помощь волонтёром</a> в кампании такого масштаба стоит больше денег.')

S['so'] = dict(
    title='Deeq bixi — Ali Verney iyo Brendan Van Alstyne oo u tartamaya Golaha Magaalada Shakopee',
    desc='Taageer ololaha Verney iyo Van Alstyne ee Golaha Magaalada Shakopee. Lacag shirkadeed ma jirto, deeq-bixiyeyaal waaweynna ma jiraan.',
    lede='Lacag shirkadeed ma jirto, deeq-bixiyeyaal waaweynna ma jiraan &mdash; ololahan wuxuu ku shaqeeyaa deriska oo bixiya wax alla wixii ay awoodaan, doolar kastana wuxuu ku hadhayaa halkan Shakopee.',
    intro='Minnesota waxay naga rabtaa inaan soo sheegno magaca, cinwaanka, iyo shaqo-bixiyaha qof kasta oo deeqihiisu sannadkii ka badan yihiin $100. PayPal ma weydiin karo dhammaan taas, sidaas darteed annagaa halkan ku weydiinayna &mdash; hal mar. Waxay qaadanaysaa qiyaastii daqiiqad, kadibna si toos ah ayaad u gudbaysaa lacag-bixinta.',
    legend_who='Cidda deeqda bixinaysa', legend_addr='Cinwaankaaga boostada',
    legend_affirm='Saddex shay oo sharcigu ku weydiinayo inaad xaqiijiso', legend_else='Wax kale?',
    l_name='Magacaaga oo dhammeystiran', h_name='Isticmaal magaca lacag-bixintaadu ku qornaan doonto, si aan labada isugu xidhno.',
    l_email='Iimaylka', h_email='Kaliya si aan kuula soo xidhiidhno haddii wax aan is waafaqsanayn ay soo baxaan marka warbixinta la gudbinayo.',
    h_addr='Tani waxay gelaysaa warbixin dadweyne oo ku saabsan maalgelinta ololaha haddii deeqahaagu sannadkii ka badnaadaan $100. Waa sharciga gobolka, ee ma aha wax aan dooranay.',
    l_street='Cinwaanka waddada', l_city='Magaalada', l_state='Gobolka', l_zip='Koodhka boostada',
    l_emp='Shaqo-bixiyaha', h_emp='Ama xirfaddaada haddii aad is-shaqaaleyso, ama kaliya &ldquo;ma shaqeeyo&rdquo; &mdash; hawlgab iyo arday labaduba way ku jiraan.',
    a1='Waxaan ahay muwaadin Mareykan ah ama qof si sharci ah loo aqbalay inuu joogo si joogto ah.',
    a2='Kani waa lacagtayda gaarka ah oo ka timid akoon shakhsi ah &mdash; ee ma aha akoon ganacsi ama shirkadeed.',
    a3='Oo ay ku jirto deeqdan, kama aan bixin wax ka badan $600 guddigan sannadka 2026.',
    l_note='Ikhtiyaari &mdash; wax kasta oo aad rabto in Brendan ogaado',
    submit='U gudub lacag-bixinta', sending='Hal daqiiqad…',
    privacy='Magacaaga, cinwaankaaga, iyo shaqo-bixiyahaagu waxay gelayaan warbixin dadweyne oo ku saabsan maalgelinta ololaha, maxaa yeelay sharciga gobolku sidaas ayuu ku qasbayaa. Iimaylkaagu ma galayo &mdash; wuxuu la joogaa ololaha, mana iibino, mana beddelno, cidnana ma siino.',
    ok_h='Mahadsanid &mdash; hal tallaabo oo kale.',
    ok_b='Waxaan haynaa waxa Minnesota naga rabto inaan soo sheegno. Hadda ku dhammee deeqdaada PayPal:',
    ok_btn='U gudub PayPal',
    ok_note='Akoon PayPal looma baahna &mdash; kaar kasta oo debit ah ama credit ah wuu shaqeeyaa. Fadlan ku deeq isla magaca aad hadda gelisay, si aan deeqdaada ugu xidhno waxaad noo sheegtay.',
    err_h='Taasi ma dhicin.',
    err_b='Wax baa dhinacayaga ka khaldamay, mana rabno inaad deeqda ku waydo. Fadlan iimayl u dir {EMAIL} ama wac ama fariin u dir {PHONE} oo waan hagaajin doonnaa.',
    unconf='<strong>Deeqaha onlaynka ah weli lama shidin.</strong> Jeegagu maanta way shaqeeyaan: ku qor magaca <strong>Brendan V for Shakopee</strong>, kadibna iimayl u dir {EMAIL} ama fariin u dir {PHONE} si aad u hesho cinwaanka boostada. Fadlan jeegaaga la socda ku dar magacaaga, cinwaankaaga, iyo shaqo-bixiyahaaga.',
    volunteer_line='Hadda ma deeqi kartid? <a href="volunteer.html">Inaad iskaa u tabarucdo</a> waxay ka qiimo badan tahay lacagta tartan sidan le\'eg.')

S['vi'] = dict(
    title='Đóng góp — Ali Verney và Brendan Van Alstyne ứng cử Hội đồng Thành phố Shakopee',
    desc='Ủng hộ chiến dịch Verney và Van Alstyne cho Hội đồng Thành phố Shakopee. Không có tiền doanh nghiệp, không có nhà tài trợ lớn.',
    lede='Không có tiền doanh nghiệp và không có nhà tài trợ lớn &mdash; chiến dịch này sống nhờ những người hàng xóm góp phần trong khả năng của mình, và từng đô la đều ở lại ngay tại Shakopee.',
    intro='Minnesota yêu cầu chúng tôi báo cáo họ tên, địa chỉ và nơi làm việc của bất kỳ ai đóng góp vượt quá $100 trong một năm. PayPal không thể hỏi hết những điều đó, nên chúng tôi hỏi &mdash; một lần, ngay tại đây. Việc này mất khoảng một phút, rồi quý vị chuyển thẳng sang thanh toán.',
    legend_who='Người đóng góp', legend_addr='Địa chỉ nhận thư của quý vị',
    legend_affirm='Ba điều luật pháp cần quý vị xác nhận', legend_else='Điều gì khác?',
    l_name='Họ và tên đầy đủ', h_name='Xin dùng đúng tên trên khoản thanh toán của quý vị, để chúng tôi đối chiếu được.',
    l_email='Email', h_email='Chỉ để liên lạc nếu có điều gì không khớp khi đến hạn nộp báo cáo.',
    h_addr='Thông tin này sẽ xuất hiện trong báo cáo tài chính vận động công khai nếu quý vị đóng góp vượt $100 trong một năm. Đó là luật tiểu bang, không phải lựa chọn của chúng tôi.',
    l_street='Địa chỉ', l_city='Thành phố', l_state='Tiểu bang', l_zip='Mã bưu điện',
    l_emp='Nơi làm việc', h_emp='Hoặc nghề nghiệp nếu quý vị tự kinh doanh, hoặc chỉ cần ghi &ldquo;không đi làm&rdquo; &mdash; nghỉ hưu và sinh viên đều được.',
    a1='Tôi là công dân Hoa Kỳ hoặc thường trú nhân hợp pháp.',
    a2='Đây là tiền của riêng tôi, từ tài khoản cá nhân &mdash; không phải tài khoản doanh nghiệp hay công ty.',
    a3='Kể cả khoản này, tôi chưa đóng góp quá $600 cho ủy ban này trong năm 2026.',
    l_note='Không bắt buộc &mdash; điều gì quý vị muốn Brendan biết',
    submit='Tiếp tục thanh toán', sending='Xin chờ một chút…',
    privacy='Họ tên, địa chỉ và nơi làm việc của quý vị sẽ xuất hiện trong báo cáo tài chính vận động công khai, vì luật tiểu bang bắt buộc. Email của quý vị thì không &mdash; email ở lại với chiến dịch, và chúng tôi không bán, không trao đổi, không đưa cho bất kỳ ai.',
    ok_h='Cảm ơn quý vị &mdash; còn một bước nữa.',
    ok_b='Chúng tôi đã có những gì Minnesota yêu cầu phải báo cáo. Bây giờ xin hoàn tất khoản đóng góp qua PayPal:',
    ok_btn='Tiếp tục sang PayPal',
    ok_note='Không cần tài khoản PayPal &mdash; mọi thẻ ghi nợ hoặc thẻ tín dụng đều dùng được. Xin đóng góp dưới đúng tên quý vị vừa nhập, để chúng tôi đối chiếu khoản đóng góp với thông tin quý vị đã cung cấp.',
    err_h='Việc gửi không thành công.',
    err_b='Có trục trặc từ phía chúng tôi, và chúng tôi không muốn quý vị mất khoản đóng góp vì điều đó. Xin gửi email tới {EMAIL} hoặc gọi hay nhắn tin tới {PHONE} và chúng tôi sẽ xử lý.',
    unconf='<strong>Đóng góp trực tuyến chưa được bật.</strong> Séc đã dùng được ngay hôm nay: ghi séc cho <strong>Brendan V for Shakopee</strong> rồi gửi email tới {EMAIL} hoặc nhắn tin tới {PHONE} để nhận địa chỉ gửi thư. Xin kèm theo séc họ tên, địa chỉ và nơi làm việc của quý vị.',
    volunteer_line='Hiện chưa thể đóng góp? <a href="volunteer.html">Làm tình nguyện viên</a> còn giá trị hơn tiền trong một cuộc đua quy mô như thế này.')

EMAIL = ('<!--email_off--><a href="mailto:brendanvanalstyne@gmail.com?subject=Donation">'
         'brendanvanalstyne@gmail.com</a><!--/email_off-->')
PHONE = '<a href="tel:+17632003711">(763) 200-3711</a>'


# The fee-coverage ask, held here as literals rather than scraped off the bio
# pages. The bio pages used to carry it, but once their Donate button started
# pointing at this form the note moved here, beside the actual handoff. A
# generator that reads its own removed source silently emits empty elements --
# which is exactly what happened once, and grep could not see it because the
# class was still present.
FEE = {
    'en': 'PayPal takes about 3% plus 49&cent; out of every gift. If you’re able, please consider covering that at checkout so your whole donation reaches the campaign.',
    'es': 'PayPal se queda con cerca del 3% más 49&cent; de cada donación. Si puede, considere cubrir ese costo al pagar para que su donación llegue completa a la campaña.',
    'fr': 'PayPal prélève environ 3&nbsp;% plus 49&cent; sur chaque don. Si vous le pouvez, pensez à couvrir ces frais au moment du paiement pour que la totalité de votre don parvienne à la campagne.',
    'ru': 'PayPal удерживает около 3% плюс 49 центов с каждого пожертвования. Если у вас есть возможность, покройте эту комиссию при оплате — тогда до кампании дойдёт вся сумма.',
    'so': 'PayPal wuxuu deeq kasta ka qaataa ku dhawaad 3% iyo 49 senti. Haddii aad awoodid, fadlan ka fiirso inaad kharashkaas daboosho markaad lacagta bixinayso si deeqdaada oo dhammi ay ololaha u gaarto.',
    'vi': 'PayPal thu khoảng 3% cộng 49 xu từ mỗi khoản đóng góp. Nếu có thể, xin quý vị cân nhắc bù phần phí đó khi thanh toán để toàn bộ khoản đóng góp đến được với chiến dịch.',
}

def read(p):
    return io.open(p, encoding='utf-8').read()


def block(text, start_re, end):
    m = re.search(start_re, text)
    if not m:
        raise SystemExit('no start for ' + start_re)
    i = m.start()
    j = text.index(end, i) + len(end)
    return text[i:j]


for loc in LOCALES:
    d = ROOT if loc == 'en' else os.path.join(ROOT, loc)
    ys = read(os.path.join(d, 'yard-sign.html'))
    br = read(os.path.join(d, 'brendan.html'))
    t = S[loc]

    header = block(ys, r'<header class="site-header">', '</header>')
    # Repoint the language switcher (and only it) at donate.html.
    header = header.replace('yard-sign.html', 'donate.html')
    footer = block(ys, r'<footer class="site-footer">', '</footer>')

    # Reuse already-live translated copy rather than retranslating it.
    hero_h1 = re.search(r'<h2 class="section-title" id="donate">(.*?)</h2>', br).group(1)
    fee_note = FEE[loc]
    rules = block(br, r'<ul class="donate-rules">', '</ul>')
    summary = re.search(r'<summary><strong>(.*?)</strong></summary>', br).group(1)

    err_b = t['err_b'].replace('{EMAIL}', EMAIL).replace('{PHONE}', PHONE)
    unconf = t['unconf'].replace('{EMAIL}', EMAIL).replace('{PHONE}', PHONE)
    base = '' if loc == 'en' else '../'
    canon = ('https://alivforshakopee.org/donate.html' if loc == 'en'
             else 'https://alivforshakopee.org/%s/donate.html' % loc)

    page = u'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{base}css/style.v5.css">
<link rel="stylesheet" href="{base}css/forms.v2.css">
<link rel="alternate" hreflang="en" href="https://alivforshakopee.org/donate.html">
<link rel="alternate" hreflang="es" href="https://alivforshakopee.org/es/donate.html">
<link rel="alternate" hreflang="fr" href="https://alivforshakopee.org/fr/donate.html">
<link rel="alternate" hreflang="ru" href="https://alivforshakopee.org/ru/donate.html">
<link rel="alternate" hreflang="so" href="https://alivforshakopee.org/so/donate.html">
<link rel="alternate" hreflang="vi" href="https://alivforshakopee.org/vi/donate.html">
<link rel="alternate" hreflang="x-default" href="https://alivforshakopee.org/donate.html">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Verney &amp; Van Alstyne for Shakopee City Council">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://alivforshakopee.org/img/og-card.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{oglocale}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://alivforshakopee.org/img/og-card.jpg">
</head>
<body>

{header}

<main>

  <div class="hero hero-volunteer">
    <div class="wrap">
      <svg class="star" style="width:56px;height:56px;margin:0 auto 0.75rem;display:block" viewBox="0 0 200 200" aria-hidden="true"><polygon fill="#f5b932" points="100,0 119.5,59.4 178.2,37.7 143.9,90 197.5,122.3 135.2,128.1 143.4,190.1 100,145 56.6,190.1 64.8,128.1 2.5,122.3 56.1,90 21.8,37.7 80.5,59.4"/></svg>
      <h1>{hero_h1}</h1>
      <p class="lede">
        {lede}
      </p>
    </div>
  </div>

  <section>
    <div class="wrap">

      <!-- Revealed by js/forms.v1.js on success. The PayPal handoff lives in
           here rather than out on the page, so the normal path records the
           donor's details before anyone reaches checkout. -->
      <div class="form-status status-ok" id="form-success" role="status" tabindex="-1" hidden>
        <h2>{ok_h}</h2>
        <p>{ok_b}</p>
        <p style="margin:1.25rem 0">
          <a class="btn" href="{paypal}">{ok_btn}</a>
        </p>
        <p class="vote-tool-note">{ok_note}</p>
        <p class="vote-tool-note donate-fee-note">{fee_note}</p>
      </div>

      <div class="form-status status-error" id="form-error" role="alert" tabindex="-1" hidden>
        <h2>{err_h}</h2>
        <p>{err_b}</p>
      </div>

      <div class="form-unconfigured" id="form-unconfigured" hidden>
        <p>{unconf}</p>
      </div>

      <p class="form-intro" data-form-intro>
        {intro}
      </p>

      <form class="form-card"
            data-signup-form
            method="post"
            action="{exec}"
            accept-charset="UTF-8">

        <input type="hidden" name="form" value="donation">
        <input type="hidden" name="lang" value="{lang}">
        <input type="hidden" name="committee" value="brendan">

        <div class="hp" aria-hidden="true">
          <label>Leave this blank
            <input type="text" name="website" tabindex="-1" autocomplete="off">
          </label>
        </div>

        <fieldset class="field-group">
          <legend>{legend_who}</legend>

          <div class="field">
            <label for="d-name">{l_name} <span class="req" aria-hidden="true">*</span></label>
            <span class="field-hint">{h_name}</span>
            <input type="text" id="d-name" name="name" autocomplete="name" required>
          </div>

          <div class="field">
            <label for="d-email">{l_email} <span class="req" aria-hidden="true">*</span></label>
            <span class="field-hint">{h_email}</span>
            <input type="email" id="d-email" name="email" autocomplete="email" required>
          </div>
        </fieldset>

        <fieldset class="field-group">
          <legend>{legend_addr}</legend>
          <span class="field-hint">{h_addr}</span>

          <div class="field">
            <label for="d-address">{l_street} <span class="req" aria-hidden="true">*</span></label>
            <input type="text" id="d-address" name="address" autocomplete="street-address" required>
          </div>

          <div class="field">
            <label for="d-city">{l_city} <span class="req" aria-hidden="true">*</span></label>
            <input type="text" id="d-city" name="city" autocomplete="address-level2" required>
          </div>

          <div class="field">
            <label for="d-state">{l_state} <span class="req" aria-hidden="true">*</span></label>
            <input type="text" id="d-state" name="state" autocomplete="address-level1" required>
          </div>

          <div class="field">
            <label for="d-zip">{l_zip} <span class="req" aria-hidden="true">*</span></label>
            <input type="text" id="d-zip" name="zip" autocomplete="postal-code" inputmode="numeric" required>
          </div>

          <div class="field">
            <label for="d-employer">{l_emp} <span class="req" aria-hidden="true">*</span></label>
            <span class="field-hint">{h_emp}</span>
            <input type="text" id="d-employer" name="employer" autocomplete="organization" required>
          </div>
        </fieldset>

        <fieldset class="field-group">
          <legend>{legend_affirm}</legend>

          <label class="check">
            <input type="checkbox" name="attest_citizen" value="on" required>
            <span>{a1}</span>
          </label>

          <label class="check">
            <input type="checkbox" name="attest_personal" value="on" required>
            <span>{a2}</span>
          </label>

          <label class="check">
            <input type="checkbox" name="attest_limit" value="on" required>
            <span>{a3}</span>
          </label>
        </fieldset>

        <fieldset class="field-group">
          <legend>{legend_else}</legend>
          <div class="field">
            <label for="d-note">{l_note}</label>
            <textarea id="d-note" name="note"></textarea>
          </div>
        </fieldset>

        <div class="form-actions">
          <button type="submit" data-sending-label="{sending}">{submit}</button>
          <p class="form-privacy">
            {privacy}
          </p>
        </div>
      </form>

      <details class="disclosure donate-disclosure" style="margin-top:2rem">
        <summary><strong>{summary}</strong></summary>
        <div class="disclosure-body">
          {rules}
        </div>
      </details>

      <p class="form-intro" style="margin-top:2rem;text-align:center">
        {volunteer_line}
      </p>

    </div>
  </section>

</main>

{footer}

<script src="{base}js/site.v3.js" defer></script>
<script src="{base}js/forms.v1.js" defer></script>
</body>
</html>
'''.format(lang=loc, title=t['title'], desc=t['desc'], base=base, canon=canon,
           oglocale=OG[loc], header=header, footer=footer, hero_h1=hero_h1,
           lede=t['lede'], intro=t['intro'], exec=EXEC, paypal=PAYPAL,
           ok_h=t['ok_h'], ok_b=t['ok_b'], ok_btn=t['ok_btn'], ok_note=t['ok_note'],
           err_h=t['err_h'], err_b=err_b, unconf=unconf,
           legend_who=t['legend_who'], legend_addr=t['legend_addr'],
           legend_affirm=t['legend_affirm'], legend_else=t['legend_else'],
           l_name=t['l_name'], h_name=t['h_name'], l_email=t['l_email'], h_email=t['h_email'],
           h_addr=t['h_addr'], l_street=t['l_street'], l_city=t['l_city'],
           l_state=t['l_state'], l_zip=t['l_zip'], l_emp=t['l_emp'], h_emp=t['h_emp'],
           a1=t['a1'], a2=t['a2'], a3=t['a3'], l_note=t['l_note'],
           sending=t['sending'], submit=t['submit'], privacy=t['privacy'],
           summary=summary, rules=rules, volunteer_line=t['volunteer_line'],
           fee_note=fee_note)

    out = os.path.join(d, 'donate.html')
    io.open(out, 'w', encoding='utf-8', newline='').write(page)
    print('wrote %-22s (%d chars)' % (out.replace(ROOT + '/', ''), len(page)))

print('\nDone.')
