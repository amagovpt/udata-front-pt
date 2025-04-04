import { Resource } from "../types/resources";
import code from '../../../templates/svg/resources/code.svg';
import archive from '../../../templates/svg/resources/archive.svg';
import documentation from '../../../templates/svg/resources/documentation.svg';
import link from '../../../templates/svg/resources/link.svg';
import table from '../../../templates/svg/resources/table.svg';
import map from '../../../templates/svg/resources/map.svg';
import globe from '../../../templates/svg/resources/globe.svg';

export function getResourceFormatIconSvg(resource: Resource): string | null {
    switch (resource.format?.trim()?.toLowerCase()) {
        case 'txt':
        case 'pdf':
        case 'rtf':
        case 'odt':
        case 'doc':
        case 'docx':
        case 'epub':
            return documentation;
        case 'json':
        case 'sql':
        case 'xml':
        case 'xsd':
        case 'shp':
        case 'kml':
        case 'kmz':
        case 'gpx':
        case 'shx':
        case 'ovr':
        case 'gpkg':
        case 'grib2':
        case 'dbf':
        case 'prj':
        case 'sqlite':
        case 'db':
        case 'sbn':
        case 'sbx':
        case 'cpg':
        case 'lyr':
        case 'owl':
        case 'dxf':
        case 'ics':
        case 'rdf':
        case 'ttl':
        case 'n3':
            return code;
        case 'tar':
        case 'gz':
        case 'tgz':
        case 'rar':
        case 'zip':
         case '7z':
         case 'xz':
         case 'bz2':
            return archive;
        case 'url':
            return link;
        case 'csv':
        case 'ods':
        case 'xls':
        case 'xlsx':
        case 'parquet':
        case 'csv.gz':
            return table;
        case 'geojson':
            return map;
        case 'ogc:wfs':
        case 'ogc:wms':
        case 'wfs':
        case 'wms':
            return globe;
        default:
            return null;
    }
}

export function getResourceTitleId(resource: Resource) {
  return 'resource-' + resource.id + '-title';
}