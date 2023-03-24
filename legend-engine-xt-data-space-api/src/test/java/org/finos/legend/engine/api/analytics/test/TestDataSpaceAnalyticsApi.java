//  Copyright 2022 Goldman Sachs
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

package org.finos.legend.engine.api.analytics.test;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.collections.api.list.ImmutableList;
import org.eclipse.collections.impl.factory.Lists;
import org.finos.legend.engine.api.analytics.DataSpaceAnalytics;
import org.finos.legend.engine.api.analytics.model.DataSpaceAnalysisInput;
import org.finos.legend.engine.language.pure.modelManager.ModelManager;
import org.finos.legend.engine.protocol.pure.PureClientVersions;
import org.finos.legend.engine.protocol.pure.v1.model.context.PureModelContextData;
import org.finos.legend.engine.shared.core.ObjectMapperFactory;
import org.finos.legend.engine.shared.core.deployment.DeploymentMode;
import org.finos.legend.engine.shared.core.operational.errorManagement.EngineException;
import org.junit.Assert;
import org.junit.Test;

import javax.ws.rs.core.Response;
import java.io.IOException;
import java.util.Objects;

public class TestDataSpaceAnalyticsApi
{
    private final DataSpaceAnalytics api = new DataSpaceAnalytics(new ModelManager(DeploymentMode.TEST));
    private static final ObjectMapper objectMapper = ObjectMapperFactory.getNewStandardObjectMapperWithPureProtocolExtensionSupports();
    private static final String minimumPureClientVersion = "v1_20_0";
    private static final ImmutableList<String> testVersions = PureClientVersions.versionsSince(minimumPureClientVersion);

    @Test
    public void testDataSpaceAnalysisWithNotFoundDataSpace() throws IOException
    {
        testVersions.forEach(pureClient ->
        {
            Exception exception = Assert.assertThrows(EngineException.class, () ->
            {
                api.analyzeDataSpace(new DataSpaceAnalysisInput(pureClient, "model::UnknownDataSpace", PureModelContextData.newPureModelContextData(null, null, Lists.immutable.empty())), null);
            });
            Assert.assertEquals(exception.getMessage(), "Can't find data space 'model::UnknownDataSpace'");
        });
    }

    @Test
    public void testDataSpaceAnalysis() throws IOException
    {
        PureModelContextData modelContextData = objectMapper.readValue(Objects.requireNonNull(getClass().getClassLoader().getResource("dataSpaceAnalyticsTestData.json")), PureModelContextData.class);
        String expected = "{\"defaultExecutionContext\":\"dummyContext\",\"description\":\"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\",\"diagrams\":[],\"elementDocs\":[],\"elements\":[],\"executables\":[],\"executionContexts\":[{\"compatibleRuntimes\":[\"model::dummyRuntime\"],\"defaultRuntime\":\"model::dummyRuntime\",\"description\":\"An important execution context\",\"mapping\":\"model::dummyMapping\",\"mappingModelCoverageAnalysisResult\":{\"mappedEntities\":[]},\"name\":\"dummyContext\"},{\"compatibleRuntimes\":[\"model::dummyRuntime2\",\"model::dummyRuntime\"],\"defaultRuntime\":\"model::dummyRuntime\",\"mapping\":\"model::dummyMapping2\",\"mappingModelCoverageAnalysisResult\":{\"mappedEntities\":[]},\"name\":\"dummyContext2\"},{\"compatibleRuntimes\":[\"model::dummyRuntime2\",\"model::dummyRuntime\"],\"defaultRuntime\":\"model::dummyRuntime2\",\"mapping\":\"model::dummyMapping2\",\"mappingModelCoverageAnalysisResult\":{\"mappedEntities\":[]},\"name\":\"dummyContext3\"}],\"featuredDiagrams\":[\"model::animal::AnimalDiagram\",\"model::GeneralDiagram\"],\"model\":{\"_type\":\"data\",\"elements\":[{\"_type\":\"profile\",\"name\":\"doc\",\"package\":\"meta::pure::profiles\",\"stereotypes\":[\"deprecated\"],\"tags\":[\"doc\",\"todo\"]},{\"_type\":\"diagram\",\"classViews\":[{\"class\":\"model::animal::reptile::Reptile\",\"id\":\"4cec85f9-9b66-450a-bdcb-c855aa0314e1\",\"position\":{\"x\":568.0,\"y\":404.0},\"rectangle\":{\"height\":58.0,\"width\":120.84765625}},{\"class\":\"model::animal::Animal\",\"id\":\"902bf14e-e7ff-40e7-92e4-8780f91bfa29\",\"position\":{\"x\":809.0,\"y\":187.0},\"rectangle\":{\"height\":44.0,\"width\":108.64453125}}],\"generalizationViews\":[{\"line\":{\"points\":[{\"x\":628.423828125,\"y\":433.0},{\"x\":863.322265625,\"y\":209.0}]},\"sourceView\":\"4cec85f9-9b66-450a-bdcb-c855aa0314e1\",\"targetView\":\"902bf14e-e7ff-40e7-92e4-8780f91bfa29\"}],\"name\":\"GeneralDiagram\",\"package\":\"model\",\"propertyViews\":[]},{\"_type\":\"class\",\"constraints\":[],\"name\":\"Animal\",\"originalMilestonedProperties\":[],\"package\":\"model::animal\",\"properties\":[{\"multiplicity\":{\"lowerBound\":1,\"upperBound\":1},\"name\":\"family\",\"stereotypes\":[],\"taggedValues\":[],\"type\":\"model::animal::Family\"},{\"multiplicity\":{\"lowerBound\":1,\"upperBound\":1},\"name\":\"noOfLegs\",\"stereotypes\":[],\"taggedValues\":[],\"type\":\"Number\"},{\"multiplicity\":{\"lowerBound\":0},\"name\":\"children\",\"stereotypes\":[],\"taggedValues\":[],\"type\":\"model::animal::GenericAnimal2\"}],\"qualifiedProperties\":[{\"body\":[{\"_type\":\"func\",\"fControl\":\"greaterThan_Number_1__Number_1__Boolean_1_\",\"function\":\"greaterThan\",\"parameters\":[{\"_type\":\"property\",\"parameters\":[{\"_type\":\"var\",\"name\":\"this\"}],\"property\":\"noOfLegs\"},{\"_type\":\"integer\",\"value\":4}]}],\"name\":\"something\",\"parameters\":[],\"returnMultiplicity\":{\"lowerBound\":1,\"upperBound\":1},\"returnType\":\"Boolean\",\"stereotypes\":[],\"taggedValues\":[]},{\"body\":[{\"_type\":\"collection\",\"multiplicity\":{\"lowerBound\":0,\"upperBound\":0},\"values\":[]}],\"name\":\"something2\",\"parameters\":[],\"returnMultiplicity\":{\"lowerBound\":0,\"upperBound\":1},\"returnType\":\"model::animal::GenericAnimal\",\"stereotypes\":[],\"taggedValues\":[]}],\"stereotypes\":[],\"superTypes\":[],\"taggedValues\":[]},{\"_type\":\"diagram\",\"classViews\":[{\"class\":\"model::animal::mammal::Mammal\",\"id\":\"641a0336-d4b5-418c-b656-2f52461264e2\",\"position\":{\"x\":427.0,\"y\":210.0},\"rectangle\":{\"height\":44.0,\"width\":125.1123046875}},{\"class\":\"model::animal::reptile::Reptile\",\"id\":\"b92253d8-0389-4c7d-b5d2-3cdc3bb1ad98\",\"position\":{\"x\":787.0,\"y\":216.0},\"rectangle\":{\"height\":58.0,\"width\":120.84765625}},{\"class\":\"model::animal::Animal\",\"id\":\"7a992cfc-c888-4091-aa00-ab430915aced\",\"position\":{\"x\":515.423828125,\"y\":-7.5},\"rectangle\":{\"height\":100.0,\"width\":199.716796875}}],\"generalizationViews\":[{\"line\":{\"points\":[{\"x\":847.423828125,\"y\":245.0},{\"x\":615.2822265625,\"y\":42.5}]},\"sourceView\":\"b92253d8-0389-4c7d-b5d2-3cdc3bb1ad98\",\"targetView\":\"7a992cfc-c888-4091-aa00-ab430915aced\"}],\"name\":\"AnimalDiagram\",\"package\":\"model::animal\",\"propertyViews\":[]},{\"_type\":\"Enumeration\",\"name\":\"Family\",\"package\":\"model::animal\",\"stereotypes\":[],\"taggedValues\":[],\"values\":[{\"stereotypes\":[],\"taggedValues\":[],\"value\":\"UO\"},{\"stereotypes\":[],\"taggedValues\":[],\"value\":\"OP\"}]},{\"_type\":\"class\",\"constraints\":[],\"name\":\"GenericAnimal\",\"originalMilestonedProperties\":[],\"package\":\"model::animal\",\"properties\":[],\"qualifiedProperties\":[],\"stereotypes\":[],\"superTypes\":[],\"taggedValues\":[]},{\"_type\":\"class\",\"constraints\":[],\"name\":\"GenericAnimal2\",\"originalMilestonedProperties\":[],\"package\":\"model::animal\",\"properties\":[],\"qualifiedProperties\":[],\"stereotypes\":[],\"superTypes\":[],\"taggedValues\":[]},{\"_type\":\"class\",\"constraints\":[],\"name\":\"Mammal\",\"originalMilestonedProperties\":[],\"package\":\"model::animal::mammal\",\"properties\":[{\"multiplicity\":{\"lowerBound\":1,\"upperBound\":1},\"name\":\"noOfLegs\",\"stereotypes\":[],\"taggedValues\":[],\"type\":\"String\"}],\"qualifiedProperties\":[],\"stereotypes\":[],\"superTypes\":[],\"taggedValues\":[]},{\"_type\":\"class\",\"constraints\":[],\"name\":\"Reptile\",\"originalMilestonedProperties\":[],\"package\":\"model::animal::reptile\",\"properties\":[{\"multiplicity\":{\"lowerBound\":1,\"upperBound\":1},\"name\":\"hasFin\",\"stereotypes\":[],\"taggedValues\":[],\"type\":\"Boolean\"}],\"qualifiedProperties\":[],\"stereotypes\":[],\"superTypes\":[\"model::animal::Animal\"],\"taggedValues\":[{\"tag\":{\"profile\":\"meta::pure::profiles::doc\",\"value\":\"doc\"},\"value\":\"\"}]}]},\"name\":\"AnimalDS\",\"package\":\"model::animal\",\"path\":\"model::animal::AnimalDS\",\"stereotypes\":[{\"profile\":\"meta::pure::profiles::doc\",\"value\":\"deprecated\"}],\"supportInfo\":{\"_type\":\"email\",\"address\":\"someEmail@test.org\"},\"taggedValues\":[{\"profile\":\"meta::pure::profiles::enterprise\",\"tag\":\"taxonomyNodes\",\"value\":\"abcdxyz005\"},{\"profile\":\"meta::pure::profiles::doc\",\"tag\":\"doc\",\"value\":\"Lorem ipsum\"},{\"profile\":\"meta::pure::profiles::doc\",\"tag\":\"doc\",\"value\":\"Lorem ipsum2\"}]}";
        testAnalyticsWithVersions(expected, modelContextData, "model::animal::AnimalDS");
    }

    private void testAnalyticsWithVersions(String expected, PureModelContextData modelContextData, String dataSpace)
    {
        testVersions.forEach(pureClient ->
        {
            Response response = api.analyzeDataSpace(new DataSpaceAnalysisInput(pureClient, dataSpace, modelContextData), null);
            Assert.assertEquals(expected, response.getEntity().toString());
        });
    }
}

