from SpazMod import tag
from SpazMod import effects
import setting

# all activites related to modify spaz by any how will be here
def main(node,player):
	_setting=setting.get_settings_data()

	if _setting['enabletags']:
		tag.addtag(node,player)
	if _setting['enablerank']:
		tag.addrank(node,player)
	if _setting['enableeffects']:
		effects.addeffect(node,player)







