import setuptools

setuptools.setup(
    name="dr_app",
    version="1.0.0",
    # scripts=["./scripts/dr_app"],
    author="Rajakumaran Arivumani",
    description="Data reconciliation app install.",
    url="https://github.com/dexplorer/df-data-recon",
    packages=["dr_app"],
    # packages = find_packages(),
    install_requires=[
        "setuptools",
        "requests",
        "utils@git+https://github.com/dexplorer/utils#egg=utils-1.0.1",
        "metadata@git+https://github.com/dexplorer/df-metadata#egg=metadata-1.0.6",
    ],
    python_requires=">=3.12",
)