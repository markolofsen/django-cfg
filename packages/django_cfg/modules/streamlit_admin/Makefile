# Streamlit Admin Module - Development Commands
#
# Usage from any Django project:
#   python manage.py gen_streamlit        - Generate + copy API clients
#   python manage.py gen_streamlit --copy-only  - Copy only (skip generation)
#   python manage.py run_streamlit        - Start Streamlit server
#   python manage.py create_streamlit_app - Scaffold new app

.PHONY: help gen gen-copy run create

PYTHON := python

help:
	@echo "Streamlit Admin - Make Commands"
	@echo ""
	@echo "  make gen       - Generate Python API clients + copy to Streamlit"
	@echo "  make gen-copy  - Copy existing clients only (skip generation)"
	@echo "  make run       - Start Streamlit server"
	@echo "  make create    - Scaffold new Streamlit app"

gen:
	$(PYTHON) manage.py gen_streamlit

gen-copy:
	$(PYTHON) manage.py gen_streamlit --copy-only

run:
	$(PYTHON) manage.py run_streamlit

create:
	$(PYTHON) manage.py create_streamlit_app
