from bs4 import BeautifulSoup
import csv
import requests


def validate_user_input(prompt):
	while True:
		try:
			userInput = int(input(prompt))
		except ValueError:
			print('Not an integer! Try again.')
			continue
		else:
			return userInput


def get_episodes(episode_number, limit):
	base_page = 'https://selfhosted.show/'
	episode_notes = []

	while True:
		url = base_page + str(episode_number)
		episode = requests.get(url)

		if episode.status_code == 200:
			print('Grabbing Episode ' + str(episode_number))
			soup = BeautifulSoup(episode.content, 'lxml')
			title = get_episode_title(episode_number, soup)
			date = get_episode_date(soup)
			notes = get_episode_notes(soup)
			formated_notes = formate_episode_notes(url, title, date, notes)
			episode_notes.append(formated_notes)
			limit -= 1

			if limit == 0:
				break
			else:
				episode_number += 1
		else:
			break

	return episode_notes


def get_episode_title(number, page):
	title = page.find('h1').text.strip()
	return str(number) + ' - ' + title.strip()


def get_episode_date(page):
	date_element = page.find('i', {'class': 'fa-calendar-alt'})
	return date_element.next_sibling.strip()


def get_episode_notes(page):
	section = page.find('div', {'class': 'split-primary prose'})
	notes = []

	for note in section.find_all('li'):
		link = ''
		for a in note.findAll('a'):
			link = a['href'].strip()

		if link != '':
			notes.append(note.text.strip() + ' - ' + link)
		else:
			notes.append(note.text.strip())

	return notes


def formate_episode_notes(url, number, date, notes):
	data = []
	for note in notes:
		data.append([url, number, date, note])

	return data


def write_notes(notes, file_name):
	print('Writing show notes to ' + file_name)
	file = open(file_name, 'w')
	with file:
		writer = csv.writer(file)
		for note in notes:
			writer.writerows(note)


if __name__ == '__main__':
	episode_number = validate_user_input('Enter an episode number: ')
	limit = validate_user_input('How many additional episodes do you want to get? -1 for the remainder: ')
	notes = get_episodes(episode_number, limit)
	output_file = 'Episode Notes.csv'
	write_notes(notes, output_file)
