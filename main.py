import discord
import os
import requests
import urllib

from bs4 import BeautifulSoup
from discord.ext import commands
from keep_alive import keep_alive
from more_itertools import grouper

client = commands.Bot(command_prefix="#")


@client.event
async def on_ready():

    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="#search movie name",
        ),
    )
    print("Bot's Ready")


async def scrapeSite(description, search_results_link, channel):
    search_results_html_page = requests.get(search_results_link).text
    search_results_soup = BeautifulSoup(search_results_html_page, 'lxml')
    search_results_movies = search_results_soup.find_all(
        'div', class_='browse-movie-wrap col-xs-10 col-sm-4 col-md-5 col-lg-4')

    for movies in grouper(search_results_movies, 10, None):
      embed = discord.Embed(
          title='RESULTS FROM YTS!',
          description=description,
          color=discord.Colour(0x2eb82e))
      url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Logo-YTS.svg/1920px-Logo-YTS.svg.png"
      embed.set_thumbnail(url=url)
      for movie in movies:
        if movie is None:
            break
        title = str(
            movie.find('a', class_='browse-movie-title').text).lower()
        year = movie.find('div', class_='browse-movie-year').text
        link = movie.find('a')['href']
        image = movie.find('img', class_='img-responsive')['src']
        rating = movie.find('h4', class_='rating').text
        categories = ', '.join(
            [el.text for el in movie.select('h4:not(.rating)')])
        embed.add_field(
            name=title.title() + f" | ({year}) | ({rating})",
            value=link,
            inline=False,
        )
        embed.add_field(name=categories, value="---" * 20)

        if (len(search_results_movies) == 1):
            embed.set_image(url=image)
      await channel.send(embed=embed)


@client.command()
async def search(ctx, *args):
    local_args = locals()
    # make arg url safe
    arg = urllib.parse.quote(str(' '.join(local_args['args'])).lower())
    search_results_link = "https://yts.mx/browse-movies/" + arg + "/all/all/0/year/0/all"
    description = 'Movie(s) you searched'
    channel = ctx.channel
    await scrapeSite(description, search_results_link, channel)


@client.command()
async def featured(ctx):
    url = 'https://yts.mx/browse-movies/0/all/all/0/featured/0/all'
    description = 'Featured Movies'
    channel = ctx.channel
    await scrapeSite(description, url, channel)


keep_alive()
client.run(os.getenv('TOKEN'))
