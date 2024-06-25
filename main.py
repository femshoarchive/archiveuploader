import logging
import discord
import os
from sys import stdout
from pathlib import Path
from git import Repo
from dotenv import load_dotenv
load_dotenv()

log = logging.getLogger("archiveuploader")
log.setLevel(logging.INFO)
handler = logging.StreamHandler(stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("[%(asctime)s|%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
log.addHandler(handler)

log.info("Checking environment...")
envmissing = False
envlist = [
    "GIT_URL",
    "GIT_PATH",
    "GIT_USER",
    "GIT_PASS",
    "DISCORD_TOKEN",
    "DISCORD_ALLOWED"
]
for env in envlist:
    if os.getenv(env) == None:
        envmissing = True
        log.error(f"Environment variable {env} isn't set!")
if envmissing:
    log.error("Environment check failed, exiting!")
    exit(1)
log.info("Environment check passed!")

repopath = os.path.join(os.path.curdir, os.getenv("GIT_PATH"))
repo: Repo

log.info("Loading repository...")
if Path(repopath).exists():
    repo = Repo(repopath)
    log.info("Repository loaded successfully!")

else:
    log.info("Unable to load repository! Removing remnants and cloning again...")
    try:
        for root, dirs, files in os.walk(repopath, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
    except Exception as e:
        log.fatal(f"Unable to remove repository remnants: {e}")
    log.info("Remnants removed! Cloning repository...")
    repo = Repo.clone_from(os.getenv("GIT_URL"), repopath)
    user = os.getenv("GIT_USER")
    password = os.getenv("GIT_PASS")
    repo.remote().set_url(os.getenv("GIT_URL").replace("//", f"//{user}:{password}@"))
    log.info("Repository cloned!")


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


@client.event
async def on_ready():
    log.info(f"Bot ({client.user.name}) connected to Discord!")
    await tree.sync()


@tree.command()
async def upload(interaction: discord.Interaction, author: str, file: discord.Attachment):
    """Create and push commit with the image"""
    await interaction.response.defer(ephemeral=True, thinking=True)
    message: discord.WebhookMessage
    if os.getenv("DISCORD_ALLOWED").find(str(interaction.user.id)) == -1:
        log.info(f"{interaction.user.name}({interaction.user.id}) tried to use the bot without permission!")
        await interaction.followup.send(embed=discord.Embed(title="Not permited", description="You are not on the whitelist!"), ephemeral=True)
        pass
    try:
        if file.content_type[:file.content_type.index("/")] != "image":
            log.info(f"{interaction.user.name}({interaction.user.id})'s file ({file.filename}) isn't an image!")
            await interaction.followup.send(embed=discord.Embed(title="Error!", description="File not an image"), ephemeral=True)
            pass
        log.info(f"{interaction.user.name}({interaction.user.id}) is uploading {file.filename} by {author}...")
        message = await interaction.followup.send(embed=discord.Embed(title="Uploading...", description="Pulling changes"), ephemeral=True)
        repo.remotes.origin.pull()
        if not Path(os.path.join(repopath, "static/art", author)).exists():
            await message.edit(embed=discord.Embed(title="Uploading...", description="Creating paths..."))
            os.makedirs(os.path.join(repopath, "static/art", author))
        await message.edit(embed=discord.Embed(title="Uploading...", description="Downloading image..."))
        await file.save(os.path.join(repopath, "static/art", author, file.filename))
        await message.edit(embed=discord.Embed(title="Uploading...", description="Commiting..."))
        repo.git.add(f"static/art/{author}/{file.filename}")
        repo.index.commit(f"Upload {file.filename} by {author} from Discord bot")
        await message.edit(embed=discord.Embed(title="Uploading...", description="Pushing..."))
        repo.remotes.origin.push()
        await message.edit(embed=discord.Embed(title="Uploaded", description="Everything's done! You'll have to wait a minute for the site to update."))
        log.info(f"{interaction.user.name}({interaction.user.id}) successfully uploaded {file.filename} by {author}!")
    except Exception as e:
        log.error(f"{interaction.user.name}({interaction.user.id}) encountered an error! {e}")
        await message.edit(embed=discord.Embed(title="Internal error encountered!", description="See server logs for more info."), ephemeral=True)

client.run(os.getenv("DISCORD_TOKEN"))

