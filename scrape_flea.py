import requests

# league_id = '124680'
league_id = '140220'
base_url = str('https://www.fleaflicker.com/nfl/leagues/')+str(league_id)


def get_league_years(league_number, html_to_parse):

    previous_years = []
    previous_seasons_list_to_parse = html_to_parse.split(str('leagues/')+str(league_number)+str('?season='))
    for y in range(2, len(previous_seasons_list_to_parse)):
        # Use "range(2," because first two elements of this list are headers:
        previous_years.append(previous_seasons_list_to_parse[y][0:4])

    # Assume blank/empty; if in middle of season then this will populate; might also populate with
    # most recent entry of "previous_years":
    this_year = []
    split_str = html_to_parse.split('data-toggle="dropdown" data-target="#">')
    this_year.append(split_str[1][0:4])

    return previous_years, this_year


def get_all_league_managers(league_number, html_to_parse, previous_years, this_year):

    df_managers = []
    return df_managers


def get_managers_for_historical_year(league_number, html_to_parse):

    df = []
    return df


def get_managers_for_current_year(html_to_parse):

    string_splits = html_to_parse.split(str('href="/users/'))
    # Skip first and last elements (first is to left of split; last is commissioner user repeated)
    user_ids = []
    user_names = []
    for xx in range(1, len(string_splits)-1):
        # Get user id (usually a six or seven digit number)
        sub_split = string_splits[xx]
        u_id = sub_split.split(str('" id="'))[0]
        user_ids.append(u_id)
        # Get user name:
        u_name_left_str = sub_split.split(str('</a>'))[0]
        # Everything to the right of ">" is the user name:
        u_name = u_name_left_str.split(str('>'))[1]
        user_names.append(u_name)

    return user_ids, user_names


def get_team_ids_for_current_year(league_number):

    # Get info from "Leaders" page
    url_leaders = str('https://www.fleaflicker.com/nfl/leagues/') + str(league_id) + str('/leaders')
    response_leaders = requests.get(url_leaders)
    leaders_html_to_parse = str(response_leaders.text)
    team_splits = leaders_html_to_parse.split(str('<a href="/nfl/leagues/')+str(league_id)+str('/teams/'))

    # Initialize to empty:
    team_ids = []
    team_names = []
    for xx in range(1, len(team_splits)):
        # One more split to isolate team id:
        sub_split = team_splits[xx].split(str('">'))
        team_ids.append(sub_split[0])
        # Last split isolates team name:
        next_split = sub_split[1].split(str('</a>'))
        team_names.append(next_split[0])

    # Do some light string replacing:
    # (1) Replace "&#39;" with "'" (single quote/apostrophe)
    # (2) Replace "&amp;" with "&"
    for xx in range(0, len(team_names)):
        team_names[xx].replace('&#39;', "'")
        team_names[xx].replace('&amp;', '&')

    return team_ids, team_names


def get_pos_and_neg_luck_for_current_year(league_number, team_id_list):

    positive_luck_sum_by_team = []
    negative_luck_sum_by_team = []
    total_luck_by_team = []

    for xx in range(0, len(team_id_list)):

        # Initialize for each team:
        all_luck_scores = []

        # HTML of "schedule" page that contains each week's luck score
        schedule_url = str('https://www.fleaflicker.com/nfl/leagues/')+\
                       str(league_number)+str('/teams/')+str(team_id_list[xx])+str('/schedule')
        response_schedule = requests.get(schedule_url)
        schedule_html_to_parse_xx = str(response_schedule.text)
        week_splits = schedule_html_to_parse_xx.split(str('</span></td><td class="right">'))

        # We'll aggregate each week's luck score into {"positive_luck_sum_by_team",
        # "negative_luck_sum_by_team", "total_luck_by_team"}.  For now initialize to zero:
        pos_luck_sum = 0
        neg_luck_sum = 0
        total_luck_sum = 0

        # Variable "week_splits" should have split html text into weeks, so iterate each week:
        # Max week 13 because we'll do playoffs as a separate function:
        for ww in range(0, min(13, len(week_splits)-1)):
            # Luck score will be the rightmost string of characters, to the right of the rightmost ">":
            sub_splits = week_splits[ww].split(str('>'))
            weekly_luck_string = sub_splits[len(sub_splits)-1]
            all_luck_scores.append(weekly_luck_string)
            # Now need to determine if "weekly_luck_string" is zero, positive or negative:
            first_character = weekly_luck_string[0]
            if first_character == str('-'):
                integer_luck = int(weekly_luck_string[1:])
                neg_luck_sum -= integer_luck
                total_luck_sum -= integer_luck
            elif first_character == str('+'):
                integer_luck = int(weekly_luck_string[1:])
                pos_luck_sum += integer_luck
                total_luck_sum += integer_luck
            else:
                if not(first_character == str(0)):
                    print(first_character)
                    raise Exception("Unanticipated string parsing...")

        # Append sums for single team to eventual output variables:
        positive_luck_sum_by_team.append(pos_luck_sum)
        negative_luck_sum_by_team.append(neg_luck_sum)
        total_luck_by_team.append(total_luck_sum)

    return positive_luck_sum_by_team, negative_luck_sum_by_team, total_luck_by_team


def main(url):

    response = requests.get(url)
    to_parse = str(response.text)
    historical_years, current_year = get_league_years(league_id, to_parse)
    user_ids_current, user_names_current = get_managers_for_current_year(to_parse)
    team_ids, team_names = get_team_ids_for_current_year(league_id)
    positive_luck_sums, negative_luck_sums, total_luck_sums = get_pos_and_neg_luck_for_current_year(league_id, team_ids)

    # Print results:
    for tt in range(0,len(team_names)):
        print(str('----------------------------------------------'))
        print(str('Team: ')+str(team_names[tt]))
        print(str('Total Negative Luck: ') + str(negative_luck_sums[tt]))
        print(str('Total Positive Luck: ') + str(positive_luck_sums[tt]))
        print(str('Sum of Negative + Positive Luck: ') + str(total_luck_sums[tt]))
        print(str('----------------------------------------------'))

    return


main(base_url)
