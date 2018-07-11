# Copyright (C) 2016-2017 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

import gzip
import lzma
import xml.etree.ElementTree

from repology.fetchers import ScratchFileFetcher
from repology.fetchers.fetch import fetch


class RepodataFetcher(ScratchFileFetcher):
    def __init__(self, url):
        super(RepodataFetcher, self).__init__(binary=True)

        self.url = url

    def do_fetch(self, statefile, logger):
        # Get and parse repomd.xml
        repomd_url = self.url + 'repodata/repomd.xml'
        logger.Log('fetching metadata from ' + repomd_url)
        repomd_content = fetch(repomd_url, check_status=True).text
        repomd_xml = xml.etree.ElementTree.fromstring(repomd_content)

        repodata_url = self.url + repomd_xml.find('{http://linux.duke.edu/metadata/repo}data[@type="primary"]/{http://linux.duke.edu/metadata/repo}location').attrib['href']

        logger.Log('fetching ' + repodata_url)
        data = fetch(repodata_url).content

        logger.GetIndented().Log('size is {} byte(s)'.format(len(data)))

        if repodata_url.endswith('gz'):
            logger.GetIndented().Log('decompressing with gzip')
            data = gzip.decompress(data)
        elif repodata_url.endswith('xz'):
            logger.GetIndented().Log('decompressing with xz')
            data = lzma.LZMADecompressor().decompress(data)

        logger.GetIndented().Log('size after decompression is {} byte(s)'.format(len(data)))

        logger.GetIndented().Log('saving')

        statefile.write(data)
