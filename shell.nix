with import <nixpkgs> {};

mkShell {
  buildInputs = [
    entr
    ffmpeg
    (python3.withPackages (ps: with ps; [
      pip
      black
      ipython
      click
      matplotlib
      pandas
      numpy
      jieba
      pkuseg
      tabulate
      wcwidth # wide chars with tabulate
      python-language-server
      pydub
      pillow
      tqdm
      joblib
    ]))
  ];
  shellHook = ''
      export REPO_DIR="$(pwd)"
      export PIP_PREFIX="$REPO_DIR/.build/pip_packages"
      export PATH="$PIP_PREFIX/bin:$PATH"
      export PYTHONPATH="$PIP_PREFIX/lib/python3.7/site-packages:$PYTHONPATH"
      export MPLBACKEND=TkAgg
      unset SOURCE_DATE_EPOCH
  '';
}
