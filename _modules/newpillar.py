# salt '*' saltutil.sync_all
# salt '*' newpillar.items
# 
import salt.utils.json
import salt.pillar
import salt.utils.crypt
import json
import ast

def items(*args, **kwargs):
    # Preserve backwards compatibility
    if args:
        return item(*args)

    pillarenv = kwargs.get("pillarenv")
    if pillarenv is None:
        if __opts__.get("pillarenv_from_saltenv", False):
            pillarenv = kwargs.get("saltenv") or __opts__["saltenv"]
        else:
            pillarenv = __opts__["pillarenv"]

    pillar_override = kwargs.get("pillar")
    pillar_enc = kwargs.get("pillar_enc")

    if pillar_override and pillar_enc:
        try:
            pillar_override = salt.utils.crypt.decrypt(
                pillar_override,
                pillar_enc,
                translate_newlines=True,
                opts=__opts__,
                valid_rend=__opts__["decrypt_pillar_renderers"],
            )
        except Exception as exc:  # pylint: disable=broad-except
            raise CommandExecutionError(
                "Failed to decrypt pillar override: {}".format(exc)
            )

    name_id = __grains__['id'].lower()
    pillar = salt.pillar.get_pillar(
        __opts__,
        dict(__grains__),
        __opts__["id"],
        pillar_override=pillar_override,
        pillarenv=pillarenv,
    )

    dict_pillar = salt.utils.json.dumps(pillar.compile_pillar())
    dict_pillar = ast.literal_eval(dict_pillar)

    key_pillar = str(dict_pillar.keys())
    key_pillar = key_pillar.replace('dict_keys([', '')
    key_pillar = key_pillar.replace("'])", "")
    key_pillar = key_pillar.replace("'", "")

    return dict_pillar[key_pillar][__opts__["id"]]
