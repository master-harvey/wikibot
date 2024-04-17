#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { WikibotStack } from '../lib/wikibot-stack';

const app = new cdk.App();
new WikibotStack(app, 'WikibotStack', {});