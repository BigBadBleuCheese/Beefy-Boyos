import sims4.commands

from beefy_boyos import hook


@sims4.commands.Command('beefyboyos.reload', command_type=sims4.commands.CommandType.Live)
def reload_settings(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    params = hook.reload()
    output('Beefy Boyos settings reloaded ({}). Details are in BeefyBoyos.log.'.format('enabled' if params['enabled'] else 'disabled'))
