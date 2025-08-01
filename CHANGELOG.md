# Changelog

## 6.2.4 (2025-06-05)

- Add noindex on security views [#693](https://github.com/datagouv/udata-front/pull/693)

## 6.2.3 (2025-05-06)

- Move CSV exports to udata [#692](https://github.com/datagouv/udata-front/pull/692/)
- Link to new admin for community resource and user profile [#682](https://github.com/datagouv/udata-front/pull/682/)

## 6.2.2 (2025-04-29)

- Use csv queryset instead of .visible for csv routes [#685](https://github.com/datagouv/udata-front/pull/685)
- Remove nofollow on internal pagination links [#686](https://github.com/datagouv/udata-front/pull/686)
- Remove noindex on list pages [#687](https://github.com/datagouv/udata-front/pull/687)
- Use target blank in resource explore [#689](https://github.com/datagouv/udata-front/pull/689)
- Remove MAAF backend (it is now directly inside udata) [#688](https://github.com/datagouv/udata-front/pull/688)
- Fix discussion tests following new closing behaviour [#690](https://github.com/datagouv/udata-front/pull/690)
- Remove old new admin and new publishing forms (move to [cdata](https://github.com/datagouv/cdata)) [#691](https://github.com/datagouv/udata-front/pull/691)

## 6.2.1 (2025-04-11)

- Use SUPPORT_URL config everywhere and modify contact us wording [#683](https://github.com/datagouv/udata-front/pull/683)
- [maaf backend] Rename is_done() function [#681](https://github.com/datagouv/udata-front/pull/681)

## 6.2.0 (2025-04-02)

- Update dependencies [#676](https://github.com/datagouv/udata-front/pull/676)
  - propagate [udata dependencie upgrade](https://github.com/opendatateam/udata/pull/3278)
  - upgrade feedparser to 6.0.11
  - upgrade python-frontmatter to 1.1.0
  - flask-themes2 to 1.0.1
  - modify code following mistune upgrade in udata
- Migrate to CaptchEtat v2 [#679](https://github.com/datagouv/udata-front/pull/679) [#680](https://github.com/datagouv/udata-front/pull/680)

## 6.1.6 (2025-03-24)

- Fix menu translation using python parenthesis format [#678](https://github.com/datagouv/udata-front/pull/678)

## 6.1.5 (2025-03-14)

- Optimize dataset detail view for dataset with many resources [#673](https://github.com/datagouv/udata-front/pull/673)
- Update dataservice type and remove unused stuff [#655](https://github.com/datagouv/udata-front/pull/655)
- Add delete_comments args when deleting a user as spam [#666](https://github.com/datagouv/udata-front/pull/666)

## 6.1.4 (2025-03-10)

- Change unavailable resource style [#670](https://github.com/datagouv/udata-front/pull/670)

## 6.1.3 (2025-03-04)

- Support null end date for temporal coverage [#411](https://github.com/datagouv/udata-front/pull/411)
- Fix dataservices edit button routing [#664](https://github.com/datagouv/udata-front/pull/664)
- Show all types of contact points [#665](https://github.com/datagouv/udata-front/pull/665/)

## 6.1.2 (2025-02-20)

- Use beta admin as default [#621](https://github.com/datagouv/udata-front/pull/621) [#662](https://github.com/datagouv/udata-front/pull/662)
- Add support for multiple contact points [#528](https://github.com/datagouv/udata-front/pull/528)
- Remove unused social network [#656](https://github.com/datagouv/udata-front/pull/656)
- Add direct link to harvest source in dataset metadata for sysadmin [#660](https://github.com/datagouv/udata-front/pull/660)

## 6.1.1 (2025-01-31)

- Fix homepage translations and links [#644](https://github.com/datagouv/udata-front/pull/644) [#648](https://github.com/datagouv/udata-front/pull/648)
- Fix security tests after udata changes [#650](https://github.com/datagouv/udata-front/pull/650)
- Add Bluesky link [#649](https://github.com/datagouv/udata-front/pull/649)
- Propagate packaging dependency upgrade from udata [#651](https://github.com/datagouv/udata-front/pull/651)

## 6.1.0 (2025-01-20)

- Fix following cache issue [#631](https://github.com/datagouv/udata-front/pull/631)
- Add dataservice search to header [#622](https://github.com/datagouv/udata-front/pull/622)
- Trigger GitLab infra deployment through simple-scaffolding script [#632](https://github.com/datagouv/udata-front/pull/632)
- Fix CI trigger GitLab pipeline job [#635](https://github.com/datagouv/udata-front/pull/635)
- New footer newsletter design [#634](https://github.com/datagouv/udata-front/pull/634)
- Fix dropdown keyboard navigation [#637](https://github.com/datagouv/udata-front/pull/637)
- New homepage [#626](https://github.com/datagouv/udata-front/pull/626)
- Add missing translations [#641](https://github.com/datagouv/udata-front/pull/641)

## 6.0.7 (2024-12-20)

- Add NATIONAL_MOURNING config [#625](https://github.com/datagouv/udata-front/pull/625)

## 6.0.6 (2024-12-09)

- Add geo specific display on OGC service resources [#609](https://github.com/datagouv/udata-front/pull/609)
- Add dataservices.csv route [#612](https://github.com/datagouv/udata-front/pull/612)
- Add csv.gz format as table resource [617](https://github.com/datagouv/udata-front/pull/617)

## 6.0.5 (2024-11-29)

- Compile udata deps to latest and upgrade lxml [#615](https://github.com/datagouv/udata-front/pull/615)

## 6.0.4 (2024-11-29)

- Disable sentry session tracking [#610](https://github.com/datagouv/udata-front/pull/610)
- Use metadata_modifed_at in dataservice cache keys [#611](https://github.com/datagouv/udata-front/pull/611)
- We don't want to fallback on site.home with params [#613](https://github.com/datagouv/udata-front/pull/613)
- Update dataset params parsing to deal with tags correctly [#614](https://github.com/datagouv/udata-front/pull/614)

## 6.0.3 (2024-11-19)

- Remove duplicated /admin in admin dataservice route [#608](https://github.com/datagouv/udata-front/pull/608)

## 6.0.2 (2024-11-19)

- Display correct business documentation url link [#595](https://github.com/datagouv/udata-front/pull/595)
- Remove old display from api.gouv.fr in datasets pages [#597](https://github.com/datagouv/udata-front/pull/597)
- Change link to reuses search page instead of datasets search page in dataservice search page [#599](https://github.com/datagouv/udata-front/pull/599)
- Add edit button in dataservice public page [#602](https://github.com/datagouv/udata-front/pull/602)
- Add dataservice search to org page [#601](https://github.com/datagouv/udata-front/pull/601)
- Add energie as featured topic [#604](https://github.com/datagouv/udata-front/pull/604)

## 6.0.1 (2024-11-13)

- Fix missing closing <a> tag in contact form [#589](https://github.com/datagouv/udata-front/pull/589)
- Fix breadcrumb link for dataservice page [#590](https://github.com/datagouv/udata-front/pull/590)
- Remove truncate and excerpt helpers function and fix error with remove-markdown [#591](https://github.com/datagouv/udata-front/pull/591)
- Add API menu item [#592](https://github.com/datagouv/udata-front/pull/592)
- Add publish button to menu [#578](https://github.com/datagouv/udata-front/pull/578)

## 6.0.0 (2024-11-07)

- Add beta admin `dataservice` page [#558](https://github.com/datagouv/udata-front/pull/558)
- Add Dataservice publishing form [#358](https://github.com/datagouv/udata-front/pull/559)
- Add the me keyword to the rel attribute of the link to the user website [#571](https://github.com/datagouv/udata-front/pull/571)
- Add dataservice access banner [#573](https://github.com/datagouv/udata-front/pull/573)
- Migrate organization badges label to lowercase [#577](https://github.com/datagouv/udata-front/pull/577)
- Use Dataservice search [#565](https://github.com/datagouv/udata-front/pull/565)
- Add organization type filter to dataset search [#579](https://github.com/datagouv/udata-front/pull/579)
- Fix Reuse tests [#580](https://github.com/datagouv/udata-front/pull/580)
- Rename private to draft [#572](https://github.com/datagouv/udata-front/pull/572) [#583](https://github.com/datagouv/udata-front/pull/583)

## 5.2.4 (2024-10-22)

- Paginate datasets in dataservice display [#560](https://github.com/datagouv/udata-front/pull/560) [#568](https://github.com/datagouv/udata-front/pull/568)
- Beta admin adjustments [#557](https://github.com/datagouv/udata-front/pull/557)
- Fix schema tooltip position [#561](https://github.com/datagouv/udata-front/pull/561)
- Add Parquet file url in download tab [#563](https://github.com/datagouv/udata-front/pull/563)

## 5.2.3 (2024-10-08)

- Adapt to discussion csv export refactor [#543](https://github.com/datagouv/udata-front/pull/543)
- Add beta admin discussion page [#539](https://github.com/datagouv/udata-front/pull/539)
- Add beta admin harvester page [#547](https://github.com/datagouv/udata-front/pull/547)
- Update beta admin members page [#544](https://github.com/datagouv/udata-front/pull/544)
- Fix Beta admin profile page [#546](https://github.com/datagouv/udata-front/pull/546)
- Add beta admin user's datasets page [#549](https://github.com/datagouv/udata-front/pull/549)
- Add beta admin user's reuses page [#550](https://github.com/datagouv/udata-front/pull/550)
- Add beta admin community resources page [#551](https://github.com/datagouv/udata-front/pull/551)
- Display contact point contact form [#555](https://github.com/datagouv/udata-front/pull/555)
- Use created_at date in reuse card [#556](https://github.com/datagouv/udata-front/pull/556)

## 5.2.2 (2024-09-23)

- Fix translations not shown [#541](https://github.com/datagouv/udata-front/pull/541)

## 5.2.1 (2024-09-23)

- Add index page with search for dataservices [#516](https://github.com/datagouv/udata-front/pull/516)
- Add beta admin datasets page [#371](https://github.com/etalab/udata-front/pull/371)
- Redirect to forum on no search results /!\ set the `DATA_SEARCH_FEEDBACK_FORM_URL` to the forum [#526](https://github.com/datagouv/udata-front/pull/526)
- Update proconnect button and link [#530](https://github.com/datagouv/udata-front/pull/530)
- Fix scroll to resource [#531](https://github.com/datagouv/udata-front/pull/531)
- Add beta admin reuses page [#527](https://github.com/datagouv/udata-front/pull/527) [#537](https://github.com/datagouv/udata-front/pull/537)
- Fix schema filter [#532](https://github.com/datagouv/udata-front/pull/532)

## 5.2.0 (2024-09-13)

- add dataservices to dataset page [#476](https://github.com/datagouv/udata-front/pull/476)
- show contact point in dataset and dataservice page [#479](https://github.com/datagouv/udata-front/pull/479)
- add email, member since and last login at to org members table [#480](https://github.com/datagouv/udata-front/pull/480)
- always show authorization_request_url if present (even on open API) [#481](https://github.com/datagouv/udata-front/pull/481)
- Show organization type [#472](https://github.com/datagouv/udata-front/pull/472)
- show permalink for community resources [#486](https://github.com/datagouv/udata-front/pull/486)
- update sentry configuration [#498](https://github.com/datagouv/udata-front/pull/498)
- update DSFR to v1.11 [#502](https://github.com/datagouv/udata-front/pull/502) [#506](https://github.com/datagouv/udata-front/pull/506)
- Replace the "MonComptePro" SSO login button with a "ProConnect" button [#482](https://github.com/datagouv/udata-front/pull/482)
  This needs the `PROCONNECT_*` related settings in `settings.py`, and an active [ProConnect flow](https://github.com/numerique-gouv/agentconnect-documentation/blob/main/doc_fs/implementation_technique.md)
- update/remove code following the datagouv/components update [#507](https://github.com/datagouv/udata-front/pull/507) [#513](https://github.com/datagouv/udata-front/pull/513)
- When disconnecting from udata, first disconnect from ProConnect if relevant [#504](https://github.com/datagouv/udata-front/pull/504)
- update privacy policy [#510](https://github.com/datagouv/udata-front/pull/510)

## 5.1.2 (2024-08-01)

- update dependencies following updated dependencies on udata [#470](https://github.com/datagouv/udata-front/pull/470)
- update `@datagouv/components` and `vue-i18n` and fix report translation [#471](https://github.com/datagouv/udata-front/pull/471)

## 5.1.0 (2024-07-30)

- Add organization edit to new admin [#412](https://github.com/datagouv/udata-front/pull/412)
- Fix markdown tables and use DSFR ones [#432](https://github.com/datagouv/udata-front/pull/432)
- Add organization selector to dataset publishing [#438](https://github.com/datagouv/udata-front/pull/438)
- Add beta admin "add member" modale [#442](https://github.com/etalab/udata-front/pull/442)
- Update dependencies from udata [#448](https://github.com/datagouv/udata-front/pull/448) [#454](https://github.com/datagouv/udata-front/pull/454)
- Add new dataset card [#445](https://github.com/datagouv/udata-front/pull/445)
- Fix tests for oembed CORS [#453](https://github.com/datagouv/udata-front/pull/453)
- Add reports [#436](https://github.com/datagouv/udata-front/pull/436)
- Switch to @datagouv/components [#439](https://github.com/datagouv/udata-front/pull/439)
- Update translations [#458](https://github.com/datagouv/udata-front/pull/458)
- use @datagouv/components v1.1.1 [#462](https://github.com/datagouv/udata-front/pull/462)

## 5.0.1 (2024-06-12)

- Fix dataset card link opening another tab [#426](https://github.com/datagouv/udata-front/pull/426)
- Use roadmap page instead of deprecated nouveautes in footer [#429](https://github.com/datagouv/udata-front/pull/429)
- Add elections as featured topic [#430](https://github.com/datagouv/udata-front/pull/430)

## 5.0.0 (2024-06-07)

- Switch MAAF backend to new sync harvest system [#409](https://github.com/datagouv/udata-front/pull/409)
- Add dataservice show page [#420](https://github.com/datagouv/udata-front/pull/420) [#424](https://github.com/datagouv/udata-front/pull/424)
- Improve design of the OrganizationSearch component [#410](https://github.com/datagouv/udata-front/pull/410)
- Add button to remove user without sending email [#418](https://github.com/datagouv/udata-front/pull/418)
- Fix display not showing in Multiselect for multi options [#416](https://github.com/datagouv/udata-front/pull/416)
- Fix dataset publishing form [#417](https://github.com/datagouv/udata-front/pull/417)

## 4.0.3 (2024-05-28)

- Add Organization publishing form [#358](https://github.com/datagouv/udata-front/pull/358)
- Fix an error that blocks datasets search filters reset [#402](https://github.com/datagouv/udata-front/pull/402)
- Componentize dataset card [#397](https://github.com/datagouv/udata-front/pull/397)
- Use udata schema endpoint [#336](https://github.com/etalab/udata-front/pull/336)

## 4.0.2 (2024-04-26)

- Update footer [#405](https://github.com/datagouv/udata-front/pull/405)

## 4.0.1 (2024-04-26)

- Update footer

## 4.0.0 (2024-04-23)

- **breaking change** Migrate to Python 3.11 [#376](https://github.com/etalab/udata-front/pull/376)
- Fix api urls locked on dev.data.gouv.fr [#401](https://github.com/datagouv/udata-front/pull/401)

## 3.5.5 (2024-04-16)

- Add beta admin member page [#374](https://github.com/etalab/udata-front/pull/374)
- Move Pagination to datagouv-components [#365](https://github.com/etalab/udata-front/pull/365)
- Add stories to Resource component [#364](https://github.com/etalab/udata-front/pull/364)
- Move Well to datagouv-components [#382](https://github.com/etalab/udata-front/pull/382)
- Add markdown editor [#351](https://github.com/etalab/udata-front/pull/351)
- Componentize quality component [#385](https://github.com/etalab/udata-front/pull/385)
- Add codes and optgroups in Multiselect to display Insee codes and Licence groups [#347] (https://github.com/etalab/udata-front/pull/347)
- Fix datastructure display in ResourceAccordion [#389](https://github.com/etalab/udata-front/pull/389)
- Order Organization's reuses by publishing date [#390](https://github.com/etalab/udata-front/pull/390)
- Upgrade vue dependency [#386](https://github.com/etalab/udata-front/pull/386)
- Fix failing captchEtat responses [#392](https://github.com/etalab/udata-front/pull/392)
- Fix release CI [#380](https://github.com/etalab/udata-front/pull/380) [#384](https://github.com/etalab/udata-front/pull/384)
- Update constants imports from `.models` to `.constants` [#375](https://github.com/etalab/udata-front/pull/375)
- Fix rename of VisibleDatasetFactory [#387](https://github.com/etalab/udata-front/pull/387)
- Add beta admin member page [#374](https://github.com/etalab/udata-front/pull/374)
- Add Administration Panel to datagouv-components [#378] (https://github.com/etalab/udata-front/pull/378)

## 3.5.4 (2024-03-20)

- Fix footer links and some translations [#366](https://github.com/etalab/udata-front/pull/366)
- Show error when dataset discussion from url doesn't exist [#367](https://github.com/etalab/udata-front/pull/367)
- Hide quality score on "work in progress" backends [#370](https://github.com/etalab/udata-front/pull/370)
- Add a new vite config for development [#372](https://github.com/etalab/udata-front/pull/372)
- Fix structure tab not shown [#369](https://github.com/etalab/udata-front/pull/369)
- Update sentry configuration to ignore aborted requests [#368](https://github.com/etalab/udata-front/pull/368)
- Fix CI not using udata release when needed [#363](https://github.com/etalab/udata-front/pull/363)

## 3.5.3 (2024-02-22)

- Show a map of datasets' spatial coverage [#354](https://github.com/etalab/udata-front/pull/354)
- Fix redirect user to auth page [#357](https://github.com/etalab/udata-front/pull/357)
- Fix tests factories for `HarvestSource`, `backend` is now required [udata#2962](https://github.com/opendatateam/udata/pull/2962)
- Fix schema is not longer a `dict` [#361](https://github.com/etalab/udata-front/pull/361) [udata#2949](https://github.com/opendatateam/udata/pull/2949)

## 3.5.2 (2024-02-15)

- Show a button to mark as no spam a discussion or a message [#352](https://github.com/etalab/udata-front/pull/352)

## 3.5.1 (2024-02-05)

- Fix vue runtime errors [#343](https://github.com/etalab/udata-front/pull/343)
- New featured topic : agriculture [#344](https://github.com/etalab/udata-front/pull/344)
- Create data.gouv.fr-components NPM package and move some `gouvfr` components to it [#324](https://github.com/etalab/udata-front/pull/324)[#350](https://github.com/etalab/udata-front/pull/350)
- Setup storybook for data.gouv.fr-components [#346](https://github.com/etalab/udata-front/pull/346)

## 3.5.0, 3.4.0 and 3.3.0 (2024-01-23)

> **Important** <br>
> These versions contain an invalid js build and are [yanked](https://pypi.org/help/#yanked) from pypi.
> The update to the next version is mandatory to have a valid js build.

- Fix dependencies according to udata's Flask-Babel migration [#300](https://github.com/etalab/udata-front/pull/300)
- User pages are back [#338](https://github.com/etalab/udata-front/pull/338)

## 3.2.12 (2023-12-15)

- Fix support menu link [#335](https://github.com/etalab/udata-front/pull/335)

## 3.2.11 (2023-12-08)

- Remove parents, children, etc. from territory views [#328](https://github.com/etalab/udata-front/pull/328)
- Add publishing form [#266](https://github.com/etalab/udata-front/pull/266) [dependabot/36](https://github.com/etalab/udata-front/security/dependabot/36) [#331](https://github.com/etalab/udata-front/pull/331)
- New featured topics : culture and education [#332](https://github.com/etalab/udata-front/pull/332)
- Fix territory sitemap [#334](https://github.com/etalab/udata-front/pull/334)
- Add header-case to validation url [#333](https://github.com/etalab/udata-front/pull/333)

## 3.2.10 (2023-12-01)

- Ignore another ResizeObserver error [#321](https://github.com/etalab/udata-front/pull/321)
- Fixed ol not appearing in descriptions [#322](https://github.com/etalab/udata-front/pull/322)
- Fix copy discussion link [#323](https://github.com/etalab/udata-front/pull/323)
- Add text-transform-none style and use lowercase k as unit [#325](https://github.com/etalab/udata-front/pull/325)

## 3.2.9 (2023-11-21)

- Update build dependencies [#309](https://github.com/etalab/udata-front/pull/309)
- Add read-more to discussions [#310](https://github.com/etalab/udata-front/pull/310)
- New footer with newsletter [#311](https://github.com/etalab/udata-front/pull/311) [#316](https://github.com/etalab/udata-front/pull/316)
- Add metric components and hooks [#260](https://github.com/etalab/udata-front/pull/260) [#313](https://github.com/etalab/udata-front/pull/313) [#314](https://github.com/etalab/udata-front/pull/314)
- Add raise_for_status on captchetat request [#318](https://github.com/etalab/udata-front/pull/318)

## 3.2.8 (2023-10-26)

- Add German translations files and French latest translations [#307](https://github.com/etalab/udata-front/pull/307)

## 3.2.7 (2023-10-26)

- Update testing dependencies [dependabot/30](https://github.com/etalab/udata-front/security/dependabot/30) [dependabot/22](https://github.com/etalab/udata-front/security/dependabot/22) [dependabot/23](https://github.com/etalab/udata-front/security/dependabot/23) [#297](https://github.com/etalab/udata-front/pull/297) [#298](https://github.com/etalab/udata-front/pull/298)
- Fix translate links in footer [#301](https://github.com/etalab/udata-front/pull/301)
- Track participez clicks [#302](https://github.com/etalab/udata-front/pull/302)
- Fix datasets search on the organization page [#303](https://github.com/etalab/udata-front/pull/303)
- Add discoverability indicator form [#304](https://github.com/etalab/udata-front/pull/304)

## 3.2.6 (2023-09-01)

- Add missing quality criterion (`all_resources_available`) [#287](https://github.com/etalab/udata-front/pull/287)
- Replace linkedin link in footer [#292](https://github.com/etalab/udata-front/pull/292)
- Use the word file instead of resource [#291](https://github.com/etalab/udata-front/pull/291)
- Update certified icon [#288](https://github.com/etalab/udata-front/pull/288)
- Add guides to the menu [#290](https://github.com/etalab/udata-front/pull/290)
- Add resource permalink [#286](https://github.com/etalab/udata-front/pull/286) [#295](https://github.com/etalab/udata-front/pull/295)
- Update read-more height on `details` toggle [#294](https://github.com/etalab/udata-front/pull/294)
- Fix preview style discrepancies [#289](https://github.com/etalab/udata-front/pull/289)

## 3.2.5 (2023-07-19)

- Fix reuse page padding for discussions and reuses section [#270](https://github.com/etalab/udata-front/pull/270)
- Fix dataset oembed links [#271](https://github.com/etalab/udata-front/pull/271)
- Hide CaptchEtat icon loader [#272](https://github.com/etalab/udata-front/pull/272)
- Update guide links [#276](https://github.com/etalab/udata-front/pull/276)
- Redirect *pages* when missing trailing slash [#278](https://github.com/etalab/udata-front/pull/278)
- Add feedback link to header and footer [#275](https://github.com/etalab/udata-front/pull/275)
- Fix actions with scroll inside full-page tabs (e.g. dataset page) [#281](https://github.com/etalab/udata-front/pull/281)
- Add data search form to search [#274](https://github.com/etalab/udata-front/pull/274)
- Upgrade pyyaml dependency to 6.0.1 in deps tree [#283](https://github.com/etalab/udata-front/pull/283)
- Set confirmed_at when creating user in MonComptePro auth [#284](https://github.com/etalab/udata-front/pull/284)

## 3.2.4 (2023-06-19)

- Fix word-wrap for dataset description [#254](https://github.com/etalab/udata-front/pull/254)
- Fix `img` folder not copied [#255](https://github.com/etalab/udata-front/pull/255)
- Add breadcrumbs to pages [#258](https://github.com/etalab/udata-front/pull/258)
- Remove cache around dataset, reuse and organization modify button [#256](https://github.com/etalab/udata-front/pull/256)
- Fix display temporal coverage on dataset page [#261](https://github.com/etalab/udata-front/pull/261)
- Fix tooltip accessibility [#259](https://github.com/etalab/udata-front/pull/259)
- Compute unavailability based on check:available instead of status logic [#267](https://github.com/etalab/udata-front/pull/267)
- Fix [dependabot/17](https://github.com/etalab/udata-front/security/dependabot/17) and [dependabot/18](https://github.com/etalab/udata-front/security/dependabot/18) [#264](https://github.com/etalab/udata-front/pull/264). These aren't udata-front vulnerabilities but only impact vite dev server (unused in `gouvfr` theme).
- Update DSFR to 1.9 [#249](https://github.com/etalab/udata-front/pull/249)
- Fix tab sequence on dataset page [#265](https://github.com/etalab/udata-front/pull/265)
- Fix button to show closed discussion [#253](https://github.com/etalab/udata-front/pull/253)
- Replace housing venti button by agricultural topic [#268](https://github.com/etalab/udata-front/pull/268)
- Fix header search [#269](https://github.com/etalab/udata-front/pull/269)

## 3.2.3 (2023-05-16)

> **Note** <br>
> This renames the `theme` root folder to `assets` and moves it inside gouvfr theme.
> This also updates most references of `udata_front/theme/gouvfr` theme to `*` to ease the usage of other themes.

- Move `theme` to `udata_front/theme/gouvfr`[#244](https://github.com/etalab/udata-front/pull/244) [#252](https://github.com/etalab/udata-front/pull/252)
- MonComptePro SSO integration [#237](https://github.com/etalab/udata-front/pull/237):
    - New button on login and register page
    - When loging in, the datastore will seek for a coresponding user on udata. If such user does not exist, she will be created.
    - Created user during SSO will not have a password. To use the user without SSO, a password reset procedure must be used.
- Handle previous format of link to discussions, e.g. from e-mails [#241](https://github.com/etalab/udata-front/pull/241)
- Add `last_update` sort in datasets page [#242](https://github.com/etalab/udata-front/pull/242)
- Fix `.fr-btn` in `.markdown` [#243](https://github.com/etalab/udata-front/pull/243)
- Add Matomo event tracking [#246](https://github.com/etalab/udata-front/pull/246)
- New scope for Captchetat piste OAuth [#250](https://github.com/etalab/udata-front/pull/250)
- Use `datetime.utcnow` to make sure to handle utc datetimes [#251](https://github.com/etalab/udata-front/pull/251)

## 3.2.2 (2023-04-18)

- New organization page [#230](https://github.com/etalab/udata-front/pull/230)[#233](https://github.com/etalab/udata-front/pull/233)
- Update the login form after Flask-Security and WTForms upgrade [#224](https://github.com/etalab/udata-front/pull/224)
- Align reuse sidebar with image [#234](https://github.com/etalab/udata-front/pull/234)
- Show relative date on dataset and resource cards [#231](https://github.com/etalab/udata-front/pull/231)
- Add version in chunk file names for cache invalidation [#239](https://github.com/etalab/udata-front/pull/239)
- Fix RGAA criterion 8.9 [#174](https://github.com/etalab/udata-front/pull/174)

## 3.2.1 (2023-03-28)

- Front modifications to display resources schema url field [#220](https://github.com/etalab/udata-front/pull/220)
- Update ventti button url [#223](https://github.com/etalab/udata-front/pull/223)
- Dataset page fixes [#219](https://github.com/etalab/udata-front/pull/219) [#229](https://github.com/etalab/udata-front/pull/229)
- Fix "informations" throughout the repo [#218](https://github.com/etalab/udata-front/pull/218)
- fix RGAA criterion 9.3 [#222](https://github.com/etalab/udata-front/pull/222)
- New reuse page [#210](https://github.com/etalab/udata-front/pull/210)
- Fix [dependabot/10](https://github.com/etalab/udata-front/security/dependabot/10) [#228](https://github.com/etalab/udata-front/pull/228)
- Fix links color [#232](https://github.com/etalab/udata-front/pull/232)

## 3.2.0 (2023-03-07)

- Upgrading packages following Flask upgrade to 2.1.2 in udata [#207](https://github.com/etalab/udata-front/pull/207)
  - Use feedgenerator for AtomFeed instead of Werkzeug deprecated helper
  - `contextfunction` and `contextfilter` from Jinja is deprecated and replaced by `pass_context`
  - Move `Flask-Themes2` dep from udata to udata-front and upgrade to 1.0.0
- Fix `@background-contrast-blue-cumulus` LESS variable [#217](https://github.com/etalab/udata-front/pull/217)

## 3.1.3 (2023-03-02)

> **Warning**
> Refactor of breadcrumb macro to be easier to use. `toolbar_class`, `breadcrum_class`, `toolbar_container` and `breadcrumb_bar` options are now removed.
> Refactor of dataset components names to match new sizes : XS (previously card), SM, MD, LG (previously search-result).
> `dataset.display.after-description` hook is now really after the description. Use new `dataset.display.after-files` hook for previous position.
- Make newsletter url configurable [#205](https://github.com/etalab/udata-front/pull/205)
- Show a warning notice when JavaScript is disabled or failed to execute [#206](https://github.com/etalab/udata-front/pull/206)
- Update lighthouse to fix security issues [#211](https://github.com/etalab/udata-front/pull/211)
- New dataset page [#181](https://github.com/etalab/udata-front/pull/181)
- Update vue-toaster dependency to avoid reported vulnerabilities [#215](https://github.com/etalab/udata-front/pull/215)

## 3.1.2 (2023-02-06)

- Use brand color for button style `tertiary-no-outline` [#199](https://github.com/etalab/udata-front/pull/199)
- Use computed dates for resources and datasets [#201](https://github.com/etalab/udata-front/pull/201)
- Fix setuptools version used in CI [#202](https://github.com/etalab/udata-front/pull/202)
- Move Pagination to `@etalab/udata-front-plugin-helpers` and add tests [#200](https://github.com/etalab/udata-front/pull/200)

## 3.1.1 (2023-01-20)

- Fix vanilla js scripts [#196](https://github.com/etalab/udata-front/pull/196)
- Remove useless published date in resource model [#198](https://github.com/etalab/udata-front/pull/198)

## 3.1.0 (2023-01-18)

> **Note** <br>
> This changes the build system from Parcel to Vite.
> This also adds a way for udata plugin to register their own vue components
> and to display them in places chosen by the current theme

- Add resource exploration preview [#169](https://github.com/etalab/udata-front/pull/169)[#180](https://github.com/etalab/udata-front/pull/180)[#183](https://github.com/etalab/udata-front/pull/183)
- Fix RGAA criterion 9.2 [#178](https://github.com/etalab/udata-front/pull/178)
- Add i18n on size suffix [#184](https://github.com/etalab/udata-front/pull/184)
- Add theme view for mail change [#192](https://github.com/etalab/udata-front/pull/192)

## 3.0.1 (2022-12-15)

- Fix Api Representation for media after CaptchEtat integration [#173](https://github.com/etalab/udata-front/pull/173)
- Add archived and private badges to dataset search results and update card style [#170](https://github.com/etalab/udata-front/pull/170)
- Fix banner links underlined twice [#171](https://github.com/etalab/udata-front/pull/171)
- Fix margins for dataset cards [#176](https://github.com/etalab/udata-front/pull/176)
- Fix text for datasets button in org page [#172](https://github.com/etalab/udata-front/pull/172)
- Add Portuguese translations [#167](https://github.com/etalab/udata-front/pull/167)
- Add email address to shared data on oauth authorize page [#175](https://github.com/etalab/udata-front/pull/175)

## 3.0.0 (2022-11-14)

- :warning: **Breaking change** Use and display harvest metadata introduced in udata 5 [#168](https://github.com/etalab/udata-front/pull/168)
- Improve search history [#162](https://github.com/etalab/udata-front/pull/162)

## 2.0.13 (2022-11-02)

- Switch from `Flask-restplus` to its fork `Flask-rest-x` [#165](https://github.com/etalab/udata-front/pull/165)
- Add CaptchEtat integration [#159](https://github.com/etalab/udata-front/pull/159)
  - new environment variables : CAPTCHETAT_BASE_URL, CAPTCHETAT_OAUTH_BASE_URL, CAPTCHETAT_CLIENT_ID and CAPTCHETAT_CLIENT_SECRET
- Fix lighthouse reported errors [#158](https://github.com/etalab/udata-front/pull/158)

## 2.0.12 (2022-10-19)

- Fix i18n errors for `/es` [#156](https://github.com/etalab/udata-front/pull/156)
- Update API card [#160](https://github.com/etalab/udata-front/pull/160)
- Create new search results component [#157](https://github.com/etalab/udata-front/pull/157)
- Remove quality score banner [#163](https://github.com/etalab/udata-front/pull/163)
- Add energy on home venti button [#164](https://github.com/etalab/udata-front/pull/164)
- Cache behavior changes [#154](https://github.com/etalab/udata-front/pull/154):
  - Organization and Reuse display page are now cached.
  - Cache keys now embed the `last_modified` object attribute. This automatically invalidates the cache when modifying the object.

## 2.0.11 (2022-09-02)

- Fix discussions text wrap [#145](https://github.com/etalab/udata-front/pull/145)
- Update Venti buttons [#146](https://github.com/etalab/udata-front/pull/146)
- :warning: @blue-470 and @blue-500 are removed
- Fix z-index value in dataset search-result template [#153](https://github.com/etalab/udata-front/pull/153) [#155](https://github.com/etalab/udata-front/pull/155)
- Fix RGAA criterion 8.2 [#147](https://github.com/etalab/udata-front/pull/147)

## 2.0.10 (2022-08-11)

- Fix dataset search result link to organization [#150](https://github.com/etalab/udata-front/pull/150)

## 2.0.9 (2022-08-10)

- Fix selected tag with wrong color [#149](https://github.com/etalab/udata-front/pull/149)

## 2.0.8 (2022-08-09)

- Add lighthouse in CircleCI [#108](https://github.com/etalab/udata-front/pull/108)
- Fix RGAA criterion 8.2 [#130](https://github.com/etalab/udata-front/pull/130)
- Add quality score [#135](https://github.com/etalab/udata-front/pull/135)

## 2.0.7 (2022-07-20)

- Fix window.dsfr.register error [#138](https://github.com/etalab/udata-front/pull/138)
- Fix featured toggle [#137](https://github.com/etalab/udata-front/pull/137)
- Iterate on search results and cards [#136](https://github.com/etalab/udata-front/pull/136)

## 2.0.6 (2022-07-08)

- Fix RGAA criterion 7.5 [#118](https://github.com/etalab/udata-front/pull/118)
- Remove map related stuff [#124](https://github.com/etalab/udata-front/pull/124)
- Fix clear button now shown on multiselect [#125](https://github.com/etalab/udata-front/pull/125)
- Add aria-current to breadcumbs [#121](https://github.com/etalab/udata-front/pull/121)
- Add missing default og:image [#127](https://github.com/etalab/udata-front/pull/127)
- Fix 500 on favicon in admin [#126](https://github.com/etalab/udata-front/pull/126)
- Update search results [#110](https://github.com/etalab/udata-front/pull/110) [#134](https://github.com/etalab/udata-front/pull/134)
- Fix test error with long reuse title [#133](https://github.com/etalab/udata-front/pull/133)
- Removed manifest logic [#129](https://github.com/etalab/udata-front/pull/129)

## 2.0.5 (2022-06-14)

- Add new menu items and change edito pages slug [#113](https://github.com/etalab/udata-front/pull/113) [#120](https://github.com/etalab/udata-front/pull/120)
- Replace news by release notes in footer [#117](https://github.com/etalab/udata-front/pull/117)
- Use DSFR container and remove custom ones [#111](https://github.com/etalab/udata-front/pull/111)

## 2.0.4 (2022-06-09)

- Add accessibility compliance status in footer [#114](https://github.com/etalab/udata-front/pull/114)
- Fix SVG display issue [#116](https://github.com/etalab/udata-front/pull/116)

## 2.0.3 (2022-06-03)

- Update search pages [#95](https://github.com/etalab/udata-front/pull/95)
- Add support for HTML in posts [#106](https://github.com/etalab/udata-front/pull/106)
- Fix RGAA criterion 1.1 [#104](https://github.com/etalab/udata-front/pull/104)
- Fix RGAA criterion 10.4 [#103](https://github.com/etalab/udata-front/pull/103)
- Add geographical page on home venti button [#109](https://github.com/etalab/udata-front/pull/109)
- Fix RGAA criterion 11.10 [#102](https://github.com/etalab/udata-front/pull/102)
- Update DSFR to 1.5.1 [#107](https://github.com/etalab/udata-front/pull/107)
  -  :warning: SVG in JS must use `bundle-text:` prefix now

## 2.0.2 (2022-04-11)

- Add harvest catalog view [#100](https://github.com/etalab/udata-front/pull/100)
- Add elections on home venti button [#101](https://github.com/etalab/udata-front/pull/101)

## 2.0.1 (2022-04-05)

- Add support for HTML static pages and more DSFR components [#96](https://github.com/etalab/udata-front/pull/96)
- Fix mobile bugs after header changes [#99](https://github.com/etalab/udata-front/pull/99)
- Fix organizationCertified error when organization is null [#98](https://github.com/etalab/udata-front/pull/98)

## 2.0.0 (2022-03-30)

### Breaking change
- :warning: Use refactored search endpoints from udata [#60](https://github.com/etalab/udata-front/pull/60)

## 1.2.5 (2022-03-29)

- Add a transport banner hook [#94](https://github.com/etalab/udata-front/pull/94)
- Add button on organization page to see all of its datasets [#93](https://github.com/etalab/udata-front/pull/93)
- Format home page numbers [#90](https://github.com/etalab/udata-front/pull/90)
- Let browsers decide what cursor to use [#89](https://github.com/etalab/udata-front/pull/89)
- Replace see more button on home page with link [#91](https://github.com/etalab/udata-front/pull/91)
- Replace Suggest with accessible combobox [#88](https://github.com/etalab/udata-front/pull/88)

## 1.2.4 (2022-03-01)

- **Deprecation**: Topics are now deprecated and will be removed in upcoming releases.
- Fix `<read-more>` component height when it contains `<img>` [#65](https://github.com/etalab/udata-front/pull/65) [#85](https://github.com/etalab/udata-front/pull/85)
- Add featured button component back for sysadmin [#79](https://github.com/etalab/udata-front/pull/79)
- Update reuse style [#52](https://github.com/etalab/udata-front/pull/52) [#81](https://github.com/etalab/udata-front/pull/81)
- Add banner to broken user page [#76](https://github.com/etalab/udata-front/pull/76)
- :warning: Button changes [#75](https://github.com/etalab/udata-front/pull/75)
  - Remove underline from button hover
  - `.btn`, `.btn-secondary` and `.btn-secondary` are removed. Use DSFR and `.fr-btn--secondary-{color}` instead.
  - `.tags` and `.tag` are removed. Use DSFR ones instead.
  - `.dropdown` is removed. Use DSFR select instead.
- Fix duplicate request on dataset search [#70](https://github.com/etalab/udata-front/pull/70) [86](https://github.com/etalab/udata-front/pull/86)
- Add banner for harvested dataset [#73](https://github.com/etalab/udata-front/pull/73)
- Change github footer link to the tickets repository [#80](https://github.com/etalab/udata-front/pull/80)
- Remove banner for the new search beta on datasets search page [#83](https://github.com/etalab/udata-front/pull/83)
- Fix RGAA criterion 7.3 [#82](https://github.com/etalab/udata-front/pull/82)
- Use avatar_url for owner [#84](https://github.com/etalab/udata-front/pull/84)
- Update resources style [#78](https://github.com/etalab/udata-front/pull/78)

## 1.2.3 (2022-01-27)

- Fix modals not working [#71](https://github.com/etalab/udata-front/pull/71)
- Fix auth messages not shown from query parameter [#68](https://github.com/etalab/udata-front/pull/68)
- Fix RGAA criterion 10.14 [#72](https://github.com/etalab/udata-front/pull/72)
- Fix thread header wrapped when title is too long [#64](https://github.com/etalab/udata-front/pull/64)

## 1.2.2 (2022-01-21)

- Fix latest modification date for dataset and resources on dataset page [#62](https://github.com/etalab/udata-front/pull/62)
- Fix hidden datasets shown on Home and Reuses [#67](https://github.com/etalab/udata-front/pull/67)
- Add temporal coverage back to dataset page [#63](https://github.com/etalab/udata-front/pull/63)
- :warning: @bg-beige is remove, use @background-contrast-grey instead
- Update colors to fix accessibility issues [#56](https://github.com/etalab/udata-front/pull/56)
- Fix missing checkbox using DSFR checkboxes [#69](https://github.com/etalab/udata-front/pull/69)

## 1.2.1 (2022-01-11)

- Change urls in Participate banner to relevant etalab guides [#53](https://github.com/etalab/udata-front/pull/53)
- Add topic information on reuse metadata and add a filter by topic on reuse search page [#50](https://github.com/etalab/udata-front/pull/50)
- Update DSFR to v1.2.1 [#45](https://github.com/etalab/udata-front/pull/45)
- :warning: `.btn-tab` is removed, use `.fr-tag` instead [57](https://github.com/etalab/udata-front/pull/57)

## 1.2.0 (2021-12-10)

- Add a banner for the new search beta on datasets search page [#43](https://github.com/etalab/udata-front/pull/43)
- :warning: Remove Issues logic in accordance with udata [#42](https://github.com/etalab/udata-front/pull/42)
- :warning: @grey-100 is now `#e5e5e5`
- Standardize organization page similar to dataset and reuse pages [#40](https://github.com/etalab/udata-front/pull/40)
- Fix RGAA criterion 10.7 Each element focusable has a visible focus [#46](https://github.com/etalab/udata-front/pull/46)
- Fix Stylemark generation to include JS files and properly include other assets [#33](https://github.com/etalab/udata-front/pull/33)
- Redirect about page to "ressources" page in menu [#48](https://github.com/etalab/udata-front/pull/48)
- Standardize article discussions and quick fixes to discussions [#41](https://github.com/etalab/udata-front/pull/41) [#51](https://github.com/etalab/udata-front/pull/51)
- Fix error on search request cancelation [#44](https://github.com/etalab/udata-front/pull/44)

## 1.1.2 (2021-11-23)

- Standardize reuse page similar to dataset page navigation quickfixes [#31](https://github.com/etalab/udata-front/pull/31)
- Move template hook logic to udata and add oauth hooks [#29](https://github.com/etalab/udata-front/pull/29)
- Add resources pagination dataset page and use DSFR pagination [#30](https://github.com/etalab/udata-front/pull/30) [#37](https://github.com/etalab/udata-front/pull/37)
- Style oauth page [#34](https://github.com/etalab/udata-front/pull/34)
- Fix horizontal scroll on mobile [#38](https://github.com/etalab/udata-front/pull/38)
- Fix gouvfr static path [#39](https://github.com/etalab/udata-front/pull/39)

## 1.1.1 (2021-10-22)

- Update README to reflect front changes [#17](https://github.com/etalab/udata-front/pull/17)
- Add Participate banner in the footer [#24](https://github.com/etalab/udata-front/pull/24)
- Fix min-height used in posts images to center them [#23](https://github.com/etalab/udata-front/pull/23)
- Update dataset page with navigation quickfixes and add DSFR components [#18](https://github.com/etalab/udata-front/pull/18)
- Implement feedbacks on quickfixes [#26](https://github.com/etalab/udata-front/pull/26)

## 1.1.0 (2021-10-12)

- Add Cypress front-end tests stub [#9](https://github.com/etalab/udata-front/pull/9)
- Add read only mode back on frontend [#10](https://github.com/etalab/udata-front/pull/10)
- Fix RGAA criterion 1.2 Each decorative image is ignored by assistive technologies. [#13](https://github.com/etalab/udata-front/pull/13)
- Add a request membership action on organization page [#12](https://github.com/etalab/udata-front/pull/12)
- Unset vue delimiters used in html templates to prevent injections [#11](https://github.com/etalab/udata-front/pull/11)
- Fix temporal coverage order in search results metadata [#14](https://github.com/etalab/udata-front/pull/14)
- VueJS multiple mount points with a global event bus [#15](https://github.com/etalab/udata-front/pull/15) [#19](https://github.com/etalab/udata-front/pull/19)
- Fix RGAA criterion 12.6 Block of contents from multiple pages can be reached or skipped [#21](https://github.com/etalab/udata-front/pull/21)

## 1.0.0 (2021-09-16)

- :warning: **breaking change**: Package renaming and new repository [#1](https://github.com/etalab/udata-front/pull/1):
  - udata-gouvfr is now udata-front
- Update feedparser following setuptools 58.0.2 release that drops support for `use_2to3` [#6](https://github.com/etalab/udata-front/pull/6)
- Show correct number of latest reuses on homepage [#3](https://github.com/etalab/udata-front/pull/3)
- Fix next value on login to prevent infinite loop [#4](https://github.com/etalab/udata-front/pull/4) [#8](https://github.com/etalab/udata-front/pull/8)

## Previous udata-gouvfr changelog

If you're migrating from udata-gouvfr, see previous changelog [here](https://github.com/etalab/udata-gouvfr/blob/master/CHANGELOG.md)
