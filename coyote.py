# coding: utf-8

import random

from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ

LIFE = 3

class Coyote:
	def set_test(self):
		self.channel_id = "CB90X2QCS"
		self.user_list = ["tarourai", "taroupati"]
		self.user_channel = {
			"tarourai":"DB90UT5PU",
			"taroupati":"DB9T45E8N"
		}
		self.user_life = {
			"taroupati": 3,
			"tarourai" : 3
		}
	def __init__(self):
		self.channel_id = ""
		self.user_list = []
		self.user_channel = {}
		self.user_life = {}
		self.alive_user = 0
		self.user_card = {}
		self.now_turn = 0
		self.now_count = 0
		# self.real_count = 0
		self.isStarted =False
		self.reset_deck()

		# テスト環境
		# self.set_test()
	
	# 誰かがコヨーテしたら手札配り直し
	def init_game(self, message):
		for name in self.user_list:
			# 負けた人には配らない
			if self.user_life[name] > 0:
				self.user_card[name] = self.cards.pop()
			else:
				self.user_card[name] = ""
		# ダイレクトメッセージで他のユーザーの手札を送信
		for name in self.user_list:
			card_info = "----------------\n他の人の手札\n"
			for other_name, card in self.user_card.items():
				life = ""
				for i in range(self.user_life[other_name]):
					life += "●"
				# 自分のカードは非公開
				if not other_name == name:
					if life == "":
						card_info += " ~" + other_name + life + " : " + card + "~ \n"
					else:
						card_info += other_name + life + " : " + card + "\n"
				else:
					if life == "":
						card_info += " ~" + other_name + life + " :~ \n"
					else:
						card_info += other_name + life + " :\n"
						
			# message.send("----------------\n他の人の手札",self.user_channel[name])				
			message.send(card_info,self.user_channel[name])
		self.now_count = 0
		# self.now_turn = random.choice(list(enumerate(self.user_list)))[0]
		message.send(f"{self.user_list[self.now_turn]}さんから開始です")
	
	# デッキをリセット
	def reset_deck(self):
		self.cards = ["-5","-5","-10",
					  "0(夜)","0","0","0",
					  "1","1","1","1",
					  "2","2","2","2",
					  "3","3","3","3",
					  "4","4","4","4",
					  "5","5","5","5",
					  "10","10","10","15","15","20",
					  "?","max->0","×2"
					  ]
		random.shuffle(self.cards)
		self.trash = []

	# 墓地確認
	def check_trash(self, message):
		if self.isStarted:
			trash_info = "墓地内容\n"
			for card in self.trash:
				trash_info += card + ","
			message.send(trash_info)

	# 合計得点を計算
	def get_total(self, message):
		max_num = -10
		max_0_flag = False
		double_flag = False
		# 特殊カードがあるかチェック
		for name, card in self.user_card.items():

			if card == "?":
				# デッキトップと入れ替え
				topdeck = self.cards.pop()
				self.trash.append(card)
				self.trash.append(topdeck)
				self.user_card[name] = topdeck
				message.send(f"? -> {topdeck}")
			elif card == "max->0":
				max_0_flag = True
			elif card == "×2":
				double_flag = True
			elif not card == "":
				# 最大数値の更新
				if card == "0(夜)":
					num = 0
				else:
					num = int(card)

				if num > max_num:
					max_num = num
		
		# 合計得点の計算
		total_num = 0
		for card in self.user_card.values():
			# 特殊カードは0点
			if not (card == "×2" or card == "max->0" or card == "0(夜)" or card == ""):
				total_num += int(card)
			# 空白以外墓地に捨てる
			if not card == "":
				self.trash.append(card)
		
		if max_0_flag:
			total_num -= max_num
		if double_flag:
			total_num *= 2
		
		# 0(夜)が捨てられてたらデッキリセット
		if "0(夜)" in self.trash:
			self.reset_deck()

		return total_num


	def participation(self, message):
		if not self.isStarted:
			# 特定のチャンネル内のメッセージだったら
			if message.body["channel"] == self.channel_id:
				user_name = message.user["real_name"]
				# 登録済みであれば
				if user_name in self.user_channel:
					if user_name in self.user_list:
						message.send(f"{user_name}さんは既に参加しています。")
					else:
						self.user_list.append(user_name)
						# 初期ライフの設定
						self.user_life[user_name] = LIFE
						message.send(f"{user_name}さんが参加しました。")
				else:
					message.send("DMで登録をしてください。")

	def registration_user(self, message):
		if not self.isStarted:
			channel = message.body["channel"]
			name = message.user["real_name"]
			self.user_channel[name] = channel
			message.send(f"{name}さんを登録しました。")

	def registration_channel(self, message):
		if not self.isStarted:
			channel = message.body["channel"]
			self.channel_id = channel
			message.send("コヨーテチャンネルとして登録しました")
	
	def reset_users(self):
		self.user_list = []
		self.user_life = {}
		self.alive_user = 0
		self.user_card = {}
		self.now_turn = 0
		self.now_count = 0

	def abort_game(self, message):
		if self.isStarted:
			# 特定のチャンネル内のメッセージだったら
			if message.body["channel"] == self.channel_id:
				message.send("コヨーテを終了します。")
				self.reset_deck()
				self.reset_users()
				self.isStarted = False
	
	def start_game(self, message):
		if not self.isStarted:
			# 参加者からだったらスタート
			# 特定のチャンネル内のメッセージだったら
			if message.body["channel"] == self.channel_id and message.user["real_name"] in self.user_list:
				random.shuffle(self.cards)

				# 最初だけスタートプレイヤーをランダムに決定
				self.now_turn = random.choice(list(enumerate(self.user_list)))[0]
				self.init_game(message)
				self.alive_user = len(self.user_list)			
				self.isStarted = True
	
	def countCoyote(self, message):
		if self.isStarted:
			# 特定のチャンネル内のメッセージだったら
			if message.body["channel"] == self.channel_id:
				text = message.body["text"]
				# 数字だったら取得
				if text.isdecimal():
					num = int(text)
					if message.user["real_name"] == self.user_list[self.now_turn]:
						if num > self.now_count:
							self.now_count = num
							self.now_turn = self.get_next_turn()
							# if len(self.user_list) > self.now_turn + 1:
							# 	self.now_turn += 1
							# else:
							# 	self.now_turn = 0
							message.send(f"次は{self.user_list[self.now_turn]}さんの手番です。")
						else:
							message.send(f"{self.now_count}よりも大きな数字にしてください。")					
					else:
						message.send(f"今は{self.user_list[self.now_turn]}さんの手番です。")

	def coyote(self, message):
		if self.isStarted:
			# 特定のチャンネル内のメッセージだったら
			if message.body["channel"] == self.channel_id:
				if self.now_count == 0:
					message.send("初手コヨーテ禁止")
				elif message.user["real_name"] == self.user_list[self.now_turn]:
					card_info = ""
					for name, card in self.user_card.items():
						card_info += name + " : " + str(card) + "\n"	
					message.send(card_info)
					real_count = self.get_total(message)
					message.send(f"正解は{real_count}です。")

					self.calc_life(real_count, message)
					if self.alive_user == 1:
						for name, life in self.user_life.items():
							if life > 0:
								message.send(f"{name}さんの勝利です。")
						self.abort_game(message)
						return 
					if len(self.trash) == 0:
						message.send("夜が出たので山札をリセットします。")
					
					# 次のゲームへ
					self.init_game(message)
				else:
					message.send(f"今は{self.user_list[self.now_turn]}さんの手番です。")
	
	def calc_life(self, real_count, message):
		# コヨーテ成功
		if real_count < self.now_count:
			message.send("コヨーテ *成功* ")
			before_turn = self.get_before_turn()
			self.user_life[self.user_list[before_turn]] -= 1
			if self.user_life[self.user_list[before_turn]] == 0:
				message.send(f"{self.user_list[before_turn]}さんが脱落しました。")
				self.alive_user -= 1
			else:
				self.now_turn = before_turn

		# コヨーテ失敗
		else:
			message.send("コヨーテ *失敗* ")
			self.user_life[self.user_list[self.now_turn]] -= 1
			if self.user_life[self.user_list[self.now_turn]] == 0:
				message.send(f"{self.user_list[self.now_turn]}さんが脱落しました。")
				self.alive_user -= 1				
				self.now_turn = self.get_next_turn()

	# 次のターンプレイヤーのindex取得
	def get_next_turn(self):
		next_turn = self.now_turn
		while True:
			if next_turn == len(self.user_list)-1:
				next_turn = 0
			else:
				next_turn += 1
			# 生きてたらその人から
			if self.user_life[self.user_list[next_turn]] > 0:
				return next_turn
	
	# 前のターンプレイヤーのindex取得
	def get_before_turn(self):
		before_turn = self.now_turn
		while True:
			if before_turn == 0:
				before_turn = len(self.user_list) -1
			else:
				before_turn -= 1
			# 生きてたらその人から
			if self.user_life[self.user_list[before_turn]] > 0:
				return before_turn
	

			
coyote_instance = Coyote()


@respond_to('参加')
def participation(message):
	coyote_instance.participation(message)

@respond_to('登録')
def registration_user(message):
	coyote_instance.registration_user(message)

@listen_to('チャンネル')
def registration_channel(message):
	coyote_instance.registration_channel(message)

@respond_to('終了')
def abort_game(message):
	coyote_instance.abort_game(message)

@listen_to('スタート')
def start_game(message):
	coyote_instance.start_game(message)

@listen_to('')
def countCoyote(message):
	coyote_instance.countCoyote(message)

@listen_to('コヨーテ')
def coyote(message):
	coyote_instance.coyote(message)

@listen_to('墓地確認')
def check_trash(message):
	coyote_instance.check_trash(message)