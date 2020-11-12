import React from 'react';
import {createUltimatePagination, ITEM_TYPES} from 'react-ultimate-pagination';

const WrapperComponent = ({children}) => (
    <ul className="pagination custom-pagination">{children}</ul>
);

const Page = ({value, isActive, onClick}) => (
    // eslint-disable-next-line
    <li className={isActive ? 'active' : null}><a href="#" onClick={onClick}>{value}</a></li>
);

const Ellipsis = ({onClick}) => (
    // eslint-disable-next-line
    <li><a href="#" onClick={onClick}>...</a></li>
);

const FirstPageLink = ({isActive, onClick}) => (
    // eslint-disable-next-line
    <li><a href="#" onClick={onClick}>&laquo;</a></li>
);

const PreviousPageLink = ({isActive, onClick}) => (
    // eslint-disable-next-line
    <li><a href="#" onClick={onClick}>&lsaquo;</a></li>
);

const NextPageLink = ({isActive, onClick}) => (
    // eslint-disable-next-line
    <li><a href="#" onClick={onClick}>&rsaquo;</a></li>
);

const LastPageLink = ({isActive, onClick}) => (
    // eslint-disable-next-line
    <li><a href="#" onClick={onClick}>&raquo;</a></li>
);

const itemTypeToComponent = {
    [ITEM_TYPES.PAGE]: Page,
    [ITEM_TYPES.ELLIPSIS]: Ellipsis,
    [ITEM_TYPES.FIRST_PAGE_LINK]: FirstPageLink,
    [ITEM_TYPES.PREVIOUS_PAGE_LINK]: PreviousPageLink,
    [ITEM_TYPES.NEXT_PAGE_LINK]: NextPageLink,
    [ITEM_TYPES.LAST_PAGE_LINK]: LastPageLink
};

const UltimatePagination = createUltimatePagination({itemTypeToComponent, WrapperComponent});
export default UltimatePagination;