# Editing microvídeos em cenas maiores

O `harum_edit.py` recebe microvídeos já aprovados e monta um master com transições curtas.

Exemplo:

```bash
python harum_edit.py shot01.mp4 shot02.mp4 shot03.mp4   --transition 0.16 --effect fade   -o HARUM_SCENE_MASTER.mp4
```

Regra editorial: transições devem ser raras e curtas. Para Harum Noir, preferir `cut`, `fade` ou `fadeblack`; movimentos de câmera e som carregam a continuidade, não efeitos chamativos.

O editor cria uma cama ambiente procedural discreta. Narração/VOICE LOCK e música podem ser adicionadas depois sem regenerar imagem.