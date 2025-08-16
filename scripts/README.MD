# Scripts

deploy/
- deploy_frontend.ps1
- deploy_backend.ps1
- deploy_menu.ps1
- update_tunnel_secret.ps1
- local_run_* (wrappers locales)

util/
- install_all.*
- check_messages.py

archive/
- docker_scripts.* (legacy)

Flujos:
Frontend solo: pwsh scripts/deploy/deploy_frontend.ps1 -Wait
Backend (imagen ya publicada): pwsh scripts/deploy/deploy_backend.ps1 -RedeployFrontend -WaitWorkflows
Backend forzando build CI: pwsh scripts/deploy/deploy_backend.ps1 -BuildImage -RedeployFrontend -WaitWorkflows
Menú: pwsh scripts/deploy/deploy_menu.ps1
