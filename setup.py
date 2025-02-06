import setuptools

setuptools.setup(
    name="dr_app",
    version="1.0.2",
    scripts=["./scripts/dr_app"],
    author="Rajakumaran Arivumani",
    description="Data reconciliation app install.",
    url="https://github.com/dexplorer/df-data-recon",
    packages=["dr_app", "dr_app.recon"],
    # packages = find_packages(),
    install_requires=[
        "setuptools",
        "requests",
        "utils@git+https://github.com/dexplorer/utils#egg=utils-1.0.3",
        "metadata@git+https://github.com/dexplorer/df-metadata#egg=metadata-1.0.9",
        "app_calendar@git+https://github.com/dexplorer/df-app-calendar#egg=app_calendar-1.0.2",
    ],
    python_requires=">=3.12",
)
