from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from .models import *
from datetime import datetime
import random
# Create your views here.

def signup(request):
    if request.method=="POST":
        print("Raw POST data:", request.POST)
        try:
            username=request.POST['username']
            password=request.POST['password1']
            confirm_password=request.POST['password2']
            email=request.POST['email']
            age=request.POST['age']
            user=User.objects.get(id=request.user.id)

            if not username or not password or not confirm_password:
                raise ValueError("username, password, and confirm password are required")

            if password != confirm_password:
                raise ValueError("Passwords do not match")
        
            data=User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            
            UserProfile.objects.create(user=user, age=age)
            
            data.save()
            return redirect ('/signin')
    
        except Exception as e:
            print(f"Error: {str(e)}")
            return render(request, 'sign_up.html', {'error': str(e)})

    return render (request,'sign_up.html')

def signin(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Login attempt for: {name}")
            
        # Authenticate
        user = authenticate(request, username=name, password=password)
       
        
        print(f"Authenticate returned: {user}")
        
        if user is not None:
            login(request, user)
            # logout(request,user)
            print(request.user.id)
            return redirect('main')
        else:
            
            
            return render(request, 'sign_in.html',{"error" : "Invalid credientials"})
    
    return render(request, 'sign_in.html')

@login_required
def main(request):
    # profile , created =UserProfile.objects.get_or_create(user=request.user)
    profile=UserProfile.objects.get_or_create(user=request.user)
    return render(request,'main.html',{'profile':profile})

@login_required
def leaderboard_view(request):
    board = User.objects.annotate(best=Max('usergamerecord__max_score')).values('username', 'best').order_by('-best')
    return render(request, 'leaderboard.html', {'board': board})

@login_required
def tournament_history_view(request):
    history = UserGameHistoriesRecord.objects.filter(user=request.user)
    return render(request, 'tournament_history.html', {'history': history})

@login_required
def new_tournament_view(request):
    tournaments = Tournament.objects.all()
    return render(request, 'new_tournament.html', {'tournaments': tournaments})

@login_required
def play_tournament(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    profile,_ = UserProfile.objects.get_or_create(user=request.user)
    current_time = datetime.now().time()
    current_date = datetime.now().date()

    # Check tournament availability
    if current_date != tournament.date or current_time < tournament.time:
        return render(request, 'play_tournament.html', {'error': 'Tournament is not available at this time.', 'tournament': tournament})

    game_record, created = UserGameRecord.objects.get_or_create(
        user=request.user, tournament=tournament, status='playing',
        defaults={'attempt_count': 0, 'max_score': None}
    )
    if created:
        
        if profile.wallet_coins < tournament.entry_fee:
            game_record.delete()  # rollback
            return render(request, 'play_tournament.html', {'error': 'Not enough coins', 'tournament': tournament})
        profile.wallet_coins -= tournament.entry_fee
        profile.save()
        UserTournamentLink.objects.create(user=request.user, tournament=tournament)
        secret = ''.join(str(random.randint(1, 9)) for _ in range(4))
        game_record.secret = secret
        game_record.save()
    else:
        secret = game_record.secret
        if not secret:
            return render(request, 'play_tournament.html', {'error': 'Game session error', 'tournament': tournament})

    feedback = None
    game_over = False
    if request.method == 'POST':
        guess = request.POST.get('guess')
        if len(guess) != 4 or not guess.isdigit() or not all('1' <= d <= '9' for d in guess):
            feedback = 'Invalid guess. Enter 4 digits from 1-9.'
        else:
            # Generate hint
            print(secret)
            hint = ""
            for i in range(4):
                if guess[i] == secret[i]:
                    hint += "* "
                elif guess[i] in secret:
                    hint += "# "
                else:
                    hint += "_ "
            hint = hint.strip()

            UserGameHistoriesRecord.objects.create(
                user=request.user, tournament=tournament,
                input=guess, output=hint, time=current_time
            )
            game_record.attempt_count += 1
            game_record.save()
            if guess == secret:
                feedback = f'You won in {game_record.attempt_count} tries!'
                game_over = True
                game_record.status = 'win'
                game_record.max_score = 10 - game_record.attempt_count
                game_record.save()
                # award prize
                profile.wallet_coins += tournament.prize
                profile.save()
            elif game_record.attempt_count >= 10:
                feedback = f'Game over! Number was {secret}'
                game_over = True
                game_record.status = 'lose'
                game_record.save()
            else:
                feedback = f"Hint: {hint}"

    history = UserGameHistoriesRecord.objects.filter(user=request.user, tournament=tournament).order_by('-created_at')
    context = {
        'tournament': tournament,
        'attempts': game_record.attempt_count,
        'history': history,
        'feedback': feedback,
        'game_over': game_over,
    }
    if game_over:
        context['secret'] = secret
    return render(request, 'play_tournament.html', context)




@login_required
def play_game(request):
    solo_tournament = Tournament.objects.get(name="Solo Game")

    game, created = UserGameRecord.objects.get_or_create(
        user=request.user,
        tournament=solo_tournament,
        status="playing",
        defaults={
            "secret": ''.join(str(random.randint(1, 9)) for _ in range(4)),
            "attempt_count": 0
        }
    )

    profile = UserProfile.objects.get(user=request.user)
    feedback = ""

    if request.method == "POST":
        guess = request.POST.get("guess")

        if len(guess) == 4 and guess.isdigit():
            hint = ""
            for i in range(4):
                if guess[i] == game.secret[i]:
                    hint += "*"
                elif guess[i] in game.secret:
                    hint += "#"
                else:
                    hint += "_"

            UserGameHistoriesRecord.objects.create(
                user=request.user,
                tournament=solo_tournament,
                input=guess,
                output=hint,
                time=datetime.now().time()
            )

            game.attempt_count += 1
            game.save()

            feedback = hint

    histories = UserGameHistoriesRecord.objects.filter(
        user=request.user,
        tournament=solo_tournament
    ).order_by("-created_at")[:10]

    return render(request, "play.html", {
        "histories": histories,
        "feedback": feedback,
        "attempts": game.attempt_count,     
        "wallet_coins": profile.wallet_coins   
    })


@login_required
def restart_game(request):
    return render (request,'play.html')


def logout_view(request):
    logout(request)
    return redirect('signin')