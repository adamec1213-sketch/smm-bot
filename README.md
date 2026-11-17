# smm-bot

Ведение Instagram, Telegram и MAX через Claude Code.

## Навыки
`.claude/skills/` — 53 маркетинговых навыка из библиотеки
[Marketing Skills](https://github.com/coreyhaines31/marketingskills) (Corey Haines, MIT, коммит 1f83744).
Claude Code подхватывает их автоматически при открытии этого репозитория.

Обновить навыки до свежей версии:

    git clone --depth 1 https://github.com/coreyhaines31/marketingskills /tmp/ms
    rm -rf .claude/skills/*/ && cp -r /tmp/ms/skills/* .claude/skills/
