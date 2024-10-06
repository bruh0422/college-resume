import discord
from discord.ext import commands

import datetime, os, io, asyncio
from captcha.image import ImageCaptcha

captcha = {}
captcha_image = {}

tz = datetime.timezone(datetime.timedelta(hours=8))

async def generate_captcha(self, obj: commands.Context | discord.Interaction | discord.Message, target: discord.User) -> discord.Message | bool | None:
    if str(target.id) not in captcha or int(datetime.datetime.now(tz=tz).timestamp()) > captcha[str(target.id)]+1200: # 未驗證或距上次驗證未滿 20 分鐘
        while True:
            verify = os.urandom(2).hex() # 生成驗證碼
            if not any(c in verify for c in ('1', '7', 'l', '0', 'o', '6', 'b', '9', 'q', '2', 'z', '5', 's')): # 檢查是否有容易混淆的字元
                break

        with io.BytesIO() as output: # 將圖片存入記憶體
            ImageCaptcha(width=200, height=100).write(verify, output)
            output.seek(0)

            captcha_image[target.id] = output.getvalue() # 紀錄在字典中供網頁使用

            embed=discord.Embed(title='🔒｜防機器人驗證', description=f'請輸入驗證碼\n如果無法檢視 請點擊[這裡](https://tofucat.bruh0422.xyz/captcha?uid={target.id})', color=0xffcc4d)
            embed.set_image(url='attachment://CAPTCHA.png')
            file = discord.File(fp=output, filename="CAPTCHA.png")
            msg = await obj.reply(embed=embed, file=file, mention_author=False)

        try: # 偵測訊息
            message: discord.Message = await self.bot.wait_for('message', check=lambda m: m.author == obj.author and m.channel == obj.channel, timeout=60.0)
        except asyncio.TimeoutError: # 超時
            embed=discord.Embed(title='❌超時', color=0xff0000)
            await msg.edit(embed=embed, attachments=[])

            return None
        else:
            if obj.channel.type != discord.ChannelType.private and obj.channel.permissions_for(obj.guild.me).manage_messages is True: # 檢查是否有刪除訊息的權限
                await message.delete() # 刪除訊息

            if message.content.lower() != verify: # 驗證失敗
                embed=discord.Embed(title='❌看來你是機器人', color=0xff0000)
                await msg.edit(embed=embed, attachments=[])

                return None
            else: # 驗證成功
                captcha[str(target.id)] = int(datetime.datetime.now(tz=tz).timestamp())
                return msg
        finally:
            if target.id in captcha_image: captcha_image.pop(target.id)
    else: # 距上次驗證未滿 20 分鐘
        return True
