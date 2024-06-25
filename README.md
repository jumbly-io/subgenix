# SubGenix

SubGenix(TM) is a video subtitle file generator.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jumbly-io/subgenix.git
cd subgenix
```

2. Build and start the Docker containers:
```bash
make rebuild
```

## Development

Set up the development environment:
```bash
make develop
```

Access a shell Poetry environment:
```bash
make shell
```

## Makefile Commands

- `make build`: Build the distribution package
- `make install`: Install the distribution package
- `make test`: Run tests
- `make format`: Format code with black
- `make lint`: Lint and type-check code with flake8, ruff and mypy
- `make image`: Build or rebuild container image
- `make help`: Display help message

## Deployment Contexts

This project has been successfully deployed and tested in the following contexts:

| **Operating System**       | **CPU**          | **GPU**                       | **Memory** | **Performance** |
|----------------------------|------------------|-------------------------------|------------|-----------------|
| Ubuntu 22.04.4 LTS (amd64) | Intel i9-14900HX | NVIDIA RTX 4090 (16GB) Mobile |  64GB DDR5 | 10 minutes of video processed in approximately 1 minute (\*) using large model on GPU. |

(\*) Time does not include model download.

## Contributing

We welcome contributions! Follow these steps:

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<your-username>/subgenix.git`
3. Create a new branch: `git checkout -b feature-branch`
4. Make your changes and commit them
5. Push to your fork: `git push origin feature-branch`
6. Open a pull request to the main repository

Please ensure you understand the license terms before contributing.

## Continuous Integration (CI)

**Note**: This feature is not yet active.

This project uses GitHub Actions for CI. The workflow builds and pushes the Docker image to Docker Hub when a new tag is pushed.

### Setting Up GitHub Secrets

To handle Docker Hub credentials securely:

1. Go to your GitHub repository
2. Navigate to Settings > Secrets > New repository secret
3. Add two secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub password

## Legal and Ethical Use

SubGenix is designed to assist in generating subtitles for video content. Use this tool responsibly and within legal bounds.

### Permitted Uses

- Personal use
- Educational purposes
- Enhancing accessibility for videos you own or have permission to modify

### Prohibited Uses

- Generating subtitles for pirated or illegally obtained videos
- Creating subtitles for unauthorized distribution

### Legal Compliance

- Comply with all applicable copyright laws and regulations
- Respect intellectual property rights of content creators and distributors

### Disclaimer

SubGenix is provided as-is, without warranty. The developers are not responsible for any misuse. By using SubGenix, you agree to use it only for lawful and ethical purposes.

## Third-Party Licenses

SubGenix(TM) uses the following open-source packages:

- [MIT License](https://opensource.org/licenses/MIT):
  - Loguru
  - OpenAI Whisper
  - MoviePy
  - Typeguard
  - pytest
  - black
  - flake8
  - ruff
  - pre-commit
  - mypy
- [BSD License](https://opensource.org/licenses/BSD-3-Clause):
  - PyTorch
- [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause):
  - Click
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0):
  - aiofiles
  - types-aiofiles
- [PSF License Agreement](https://docs.python.org/3/license.html):
  - Python
- [MIT License](https://opensource.org/licenses/MIT) and [MPL 2.0 (Mozilla Public License 2.0)](https://www.mozilla.org/en-US/MPL/2.0/):
  - tqdm

Please see the linked license texts for full details.

## License

SubGenix(TM) itself is dual-licensed under the JMDOTS-DUAL-LICENSE-1.2:

1. **Personal, Non-Commercial License**: GNU Affero General Public License (AGPL) version 3 or later.
2. **Commercial License**: Available for business, commercial, enterprise, or governmental use.

For full license details, see the [JMDOTS-DUAL-LICENSE-1.2](https://legal.jmdots.com/licenses/).

For commercial licensing information, contact [sales@jmdots.com](mailto:sales@jmdots.com) or visit [JMDOTS GitHub](http://www.github.com/jmdots/).

```
====================================================
subgenix - SubGenix is a video to subtitle generator
====================================================
Copyright © 2024 Joshua M. Dotson (contact@jmdots.com), Mark L. Dotson (mdotson888@gmail.com)

JMDOTS-DUAL-LICENSE-1.2
=======================
https://legal.jmdots.com/licenses/

Personal, Non-Commercial License
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This software is provided under the GNU Affero General Public License (AGPL)
version 3 or later. You are free to use, modify, and distribute this
software for personal, non-commercial use under the terms of the AGPL. If you
modify this software and distribute it, you must also make the modified
source code available under the same license terms. There is no warranty for
this software, to the extent permitted by applicable law.

For more details, please refer to the full text of the GNU AGPL: [GNU Affero
General Public License](http://www.gnu.org/licenses/)

Commercial License
~~~~~~~~~~~~~~~~~~
This software is available under a Commercial License for any business,
commercial, enterprise, or governmental use. The Commercial License allows
you to use, modify, and distribute this software in proprietary applications
without the requirement to disclose source code modifications or derivative
works. Under this license, you receive additional support and maintenance
services.

For information on purchasing a commercial license, please contact us at
[sales@jmdots.com](mailto:sales@jmdots.com) or visit our website at [JMDOTS
GitHub](http://www.github.com/jmdots/).

Limited Liability
~~~~~~~~~~~~~~~~~
In no event shall the authors or copyright holders be liable for any claim,
damages, or other liability arising from the use or distribution of this
software.
```

## Contact

For questions or support, please open an issue on the GitHub repository or contact the maintainers directly.
