import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


import random
from backend.models import *
from string import ascii_lowercase
from datetime import date, timedelta
from backend.functions import get_next_surgery_day

def get_word_random():
    return ''.join([random.choice(ascii_lowercase) for _ in range(random.randint(8, 12))])


for user in CustomUser.objects.all():
    br8 = Branch.objects.get(branch_number=8)
    br9 = Branch.objects.get(branch_number=9)
    user.branches.add(br8)
    user.branches.add(br9)
    user.save()

exit()

for i in Surgeon.objects.all():
    if not i.branch:
        i.delete()


for i in range(100):
    s = Surgeon(
        full_name = get_word_random().capitalize() + ' ' + get_word_random().capitalize(),
        branch = random.choice(Branch.objects.all())
    )
    s.save()
    print(s)


for br in Branch.objects.all():
    for i in range(10):
        branch = random.choice(Branch.objects.all())
        surgery = Surgery(branch=branch,
                full_name=get_word_random().capitalize() + ' ' + get_word_random().capitalize(),
                age=random.randint(20, 60),
                diagnost=get_word_random(),
                surgery_name=random.choice(SurgeryName.objects.all()),
                surgery_type=random.choice(SurgeryType.objects.all()),
                date_of_surgery=get_next_surgery_day())
        surgery.save()
        for _ in range(random.randint(1, 5)):
            surgery.surgeons.add(random.choice(Surgeon.objects.all()))
        
        surgery.save()
        print(surgery)





# print('{')

# for i in range(4, 12):
#     username = f'surgery{i}'
#     password = f'medical{i}'
#     first_name = f'Surgery{i}'
#     last_name = f'Surgery{i}'

#     user = CustomUser(
#         username=username,
#         first_name=first_name,
#         last_name=last_name,
#         role='заведующий',
#         is_staff=True,
#         is_superuser=False
#     )
#     user.set_password(password)
#     user.save()
#     print(f'"{username}": "{password}"')

# print('}')

# head = CustomUser.objects.get(id=12)

# print(head)

# br = Branch(
#     name = 'сосудистая хирургия',
#     head = head,
#     branch_number = 12,
# )

# br.save()

# print(br.name)
# print(br.head)
# print(br.branch_number)




