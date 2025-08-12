from ..pages.models import Team


def create_team(team):
    Team.objects.create(first_name=team.first_name, last_name=team.last_name, designation=team.designation, photo=team.photo, facebock_link=team.facebock_link, twiter_link=team.twiter_link, google_plus_link=team.google_plus_link)



def list_team():
    return Team.objects.all()


def list_team_id(id):
    return Team.objects.get(id=id)